# Data Mart PostgreSQL : modélisation et écritures idempotentes

Modèle SQL : [../assets/datamart.example.sql](../assets/datamart.example.sql).

## Sommaire
1. Schémas et rôles
2. Tables d'état courant
3. Registre des lots et rejets
4. Dimensions
5. Faits d'enrôlement
6. Recalcul sans double comptage
7. Règles métier documentées
8. Migrations

## 1. Schémas et rôles

| Schéma | Contenu | Écrit par | Lu par |
|---|---|---|---|
| `etat` | État courant des tables MOSIP capturées (colonnes retenues seulement) | rôle du pipeline | pipeline, audit |
| `pipeline` | Registre des lots, rejets, contrôles qualité, correspondances de codes | rôle du pipeline (+ métier pour les correspondances, via migration) | pipeline, audit |
| `bi` | Dimensions et faits consommés par l'API et l'outil BI, fraîcheur des sources | rôle du pipeline | rôle de l'API (lecture seule), outil BI |

Rôles distincts : propriétaire des migrations, rôle d'écriture du pipeline (pas de DDL), rôle de l'API en lecture
seule sur `bi`, rôle d'audit en lecture. Aucun accès de l'API ou de l'outil BI à `etat` : il contient des clés
techniques MOSIP.

Dans ce dépôt, le schéma `bi` et ses migrations Flyway existent déjà
(`backend/src/main/resources/db/migration/`). Ajouter `etat` et `pipeline` par de nouvelles migrations, sans
modifier les migrations appliquées.

## 2. Tables d'état courant

Une table par table MOSIP capturée, même clé primaire, colonnes retenues seulement, plus :

| Colonne | Rôle |
|---|---|
| `_lsn bigint not null` | LSN du dernier événement appliqué (garde d'idempotence) |
| `_supprime boolean not null default false` | Suppression logique (événement `d`) |
| `_maj_pipeline timestamptz not null default now()` | Dernière écriture par le pipeline |
| `_source_ts timestamptz` | `source.ts_ms` de l'événement (fraîcheur et retard) |

Upsert type :

```sql
insert into etat.registration as cible (id_pseudo, reg_type, status_code, ..., _lsn, _supprime, _source_ts)
values (...)
on conflict (id_pseudo) do update
   set reg_type = excluded.reg_type, status_code = excluded.status_code, ...,
       _lsn = excluded._lsn, _supprime = false, _source_ts = excluded._source_ts, _maj_pipeline = now()
 where excluded._lsn > cible._lsn;
```

La clé de l'état courant est l'empreinte HMAC-SHA-256 de la clé MOSIP, calculée par le job Spark avec une clé
secrète (la clé Kafka arrive en clair : Debezium ne masque pas les clés de message). Elle reste unique et stable sans
exposer le RID. Les attributs utiles (centre, machine) sont dérivés du RID dans le job avant pseudonymisation ; seuls
l'empreinte et les dérivés sont stockés.

## 3. Registre des lots et rejets

- `pipeline.lot_traite (requete, lot_id, traite_le, nb_upserts, nb_suppressions, nb_ignores, nb_rejets)`,
  clé (`requete`, `lot_id`). Inséré dans la même transaction que les écritures du lot.
- `pipeline.evenement_rejete (requete, lot_id, topic, partition, kafka_offset, motif, empreinte, rejete_le)` :
  jamais le contenu du message.
- `pipeline.controle_qualite (controle, execute_le, statut, valeur, seuil, detail)` : résultat de chaque contrôle.

## 4. Dimensions

- **Territoire** : `bi.zone` (déjà présente) alimentée depuis `master.location` (niveaux via `hierarchy_level`,
  parent via `parent_loc_code`) et `master.registration_center` (`location_code`). Toujours filtrer une langue de
  référence (`lang_code`) : les tables `master` sont multilingues. Les codes du référentiel remplacent les codes
  provisoires de développement.
- **Centre** : identifiant du centre ; s'il est dérivé du préfixe du RID, contrôler le taux de correspondance avec
  `master.registration_center` (un centre inconnu va dans « centre non référencé », jamais perdu dans une jointure).
- **Période** : jour (et semaine ISO, mois, année dérivés). La date retenue (`pkt_cr_dtimes` = création du paquet au
  centre, ou `cr_dtimes` = réception par MOSIP) est une règle métier à écrire dans le dictionnaire.
- **Type d'opération** : `registration.reg_type` (valeurs relevées sur l'instance, libellés validés).
- **Statut** : regroupement des codes MOSIP via `pipeline.correspondance_statut (status_code, latest_trn_status_code,
  statut_regroupe, valide_par, valide_le)` ; code absent → `non_classe` + alerte.
- **Sexe, tranche d'âge** : pas de source anonyme en MOSIP 1.1.5 (voir [mosip-115.md](mosip-115.md) § 3). Valeur
  `I` / `inconnu` et note visible dans le BI tant qu'une source n'est pas décidée.

## 5. Faits d'enrôlement

Deux lectures possibles de « par statut, chaque jour », à trancher avec le demandeur avant de modéliser :

| Lecture | Question | Modèle |
|---|---|---|
| Cohorte (défaut du BI de l'ANID : « devenir des inscriptions ») | Les inscriptions du jour J, où en sont-elles aujourd'hui ? | Fait recalculé depuis l'état courant (§ 6) ; les chiffres d'un jour passé évoluent quand les dossiers avancent |
| Photo | Combien de dossiers étaient dans chaque statut à la fin du jour J ? | Table d'instantanés `bi.photo_statut_jour`, alimentée une fois par jour depuis l'état courant, jamais réécrite ; pas de reconstitution possible du passé sans historique des transactions |

Grain recommandé pour la cohorte : jour × centre × type d'opération × statut regroupé (× sexe × tranche d'âge quand
la source existe), avec le nombre d'inscriptions. Région, préfecture… s'obtiennent par la dimension territoire : ne pas stocker
la région dans le fait, sinon un changement de rattachement d'un centre fausse l'historique.

Si une table de faits « large » existe déjà (ex. `bi.fait_enrolement_jour` avec une colonne par statut), la
conserver et l'alimenter depuis le même calcul ; ne pas créer deux sources pour un même chiffre.

Contrôles intégrés au calcul : somme des statuts = total des inscriptions ; aucune valeur négative ; aucun centre
perdu (inscriptions de l'état courant = inscriptions des faits).

## 6. Recalcul sans double comptage

Les faits sont toujours **dérivés de l'état courant**, jamais incrémentés par événement. Deux façons, à choisir selon
la fraîcheur voulue :

1. **Recalcul des clés touchées dans la transaction du lot** (fraîcheur de l'ordre de la minute) : relever les clés
   de faits (jour, centre, type…) des lignes du lot **avant et après** l'upsert (un changement de statut déplace
   une inscription d'une case à l'autre), supprimer puis réinsérer ces cases à partir de `etat`. Rejouer le lot
   redonne les mêmes cases.
2. **Recalcul complet périodique** (vue matérialisée ou table reconstruite dans une transaction, ex. toutes les
   15 minutes) : plus simple, assez rapide pour quelques millions de lignes. `REFRESH MATERIALIZED VIEW CONCURRENTLY`
   demande un index unique.

Dans les deux cas, un recalcul complet nocturne compare ses résultats aux faits courants (contrôle de dérive).

Mettre à jour `bi.source_fraicheur` (dernière donnée = `max(_source_ts)` de la source, dernier chargement = fin du
lot) dans la même transaction : la pastille « Dernière mise à jour » du BI en dépend.

## 7. Règles métier documentées

Chaque indicateur a sa fiche dans `docs/indicateurs.md` (définition, calcul, dénominateur, source exacte, règle de
date, traitement des suppressions, statut de validation). Le code cite le code de la fiche (ex. `E-NIU`) en
commentaire. Une règle non validée par l'équipe MOSIP reste marquée « à confirmer » et s'affiche comme telle.

## 8. Migrations

- Additives : nouvelles tables, nouvelles colonnes nullable, nouveaux index (`create index concurrently` hors
  transaction si la table est grosse).
- Jamais modifier une migration appliquée ; en créer une nouvelle.
- Destructif (`drop`, changement de type, `delete` massif, renommage) : script séparé, plan de retour arrière,
  sauvegarde vérifiée, validation explicite. Proposer d'abord une transition (nouvelle colonne, double écriture,
  bascule, suppression plus tard).
- Reconstruction d'un état courant : dans une nouvelle table, comparée à l'ancienne, puis bascule ; pas de
  `truncate` de la table en service.
