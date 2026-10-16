---
name: mosip-bi-pipeline
description: >-
  Conception, implémentation et maintenance du pipeline de reporting MOSIP 1.1.5 : EDB PostgreSQL → Debezium →
  Kafka → PySpark Structured Streaming → Data Mart PostgreSQL → BI. À utiliser dès qu'une tâche touche la capture
  de changements (CDC) des bases MOSIP (mosip_regprc, mosip_master, mosip_idrepo, mosip_prereg, mosip_ida…),
  un connecteur Debezium, un slot logique, une publication, le WAL, un topic Kafka, un job Spark de streaming,
  les checkpoints, les écritures idempotentes ou les tables du Data Mart et les indicateurs d'enrôlement
  (centre, sexe, région, période, type d'opération, statut). Aussi pour les tests et contrôles qualité du pipeline,
  la protection des données personnelles et biométriques, l'observabilité (retard CDC, WAL retenu, lag Kafka,
  fraîcheur BI) et la documentation d'exploitation. Même si l'utilisateur ne cite ni Debezium ni Spark, utiliser
  ce skill pour toute question « d'où vient ce chiffre » ou « pourquoi le BI n'est plus à jour ».
compatibility: >-
  Claude Code. Cible : MOSIP 1.1.5 sur EDB Postgres Advanced Server, Debezium 3.x (connecteur PostgreSQL, pgoutput),
  Kafka, Spark 4.x (PySpark, Python 3.10+, Java 17/21), PostgreSQL pour le Data Mart.
---

# Pipeline de reporting MOSIP 1.1.5

Ce skill guide la conception et la maintenance du pipeline qui alimente le BI de l'ANID à partir de MOSIP 1.1.5 :

```
EDB PostgreSQL (MOSIP, lecture seule)
  → Debezium (connecteur PostgreSQL, pgoutput, un slot logique par connecteur)
  → Kafka (un topic par table capturée, clé = clé primaire)
  → PySpark Structured Streaming (état courant des tables, idempotent)
  → Data Mart PostgreSQL (état courant, faits agrégés, contrôles)
  → API et interface BI (backend/, frontend/)
```

## Règles non négociables

Ces règles passent avant toute demande de vitesse. Elles existent parce que le pipeline touche un système d'identité
nationale : une erreur peut remplir le disque de la base MOSIP de production, fausser des chiffres publiés ou exposer
des données personnelles.

1. **Claude n'agit jamais lui-même sur la production.** Créer ou supprimer un slot, une publication ou un rôle,
   changer `wal_level` ou un paramètre, lancer un snapshot, démarrer un connecteur, écrire dans une base MOSIP :
   Claude prépare le script ou la demande (effet, risques, retour arrière) ; l'équipe responsable (DBA,
   exploitation) l'exécute après validation de cette action précise. Une autorisation générale donnée d'avance
   (« tu peux créer le slot si besoin ») ne suffit pas : la signaler et préparer la demande. En recette, mêmes
   préparations ; Claude n'exécute que si l'humain le demande explicitement pour cette action et cet environnement.
2. **Aucune migration destructive sans validation** (`DROP`, `TRUNCATE`, `DELETE` massif, changement de type, purge
   de topic, suppression de checkpoint ou de slot). Toujours proposer d'abord une variante additive.
3. **Ne jamais inventer de table ni de colonne MOSIP.** Toute table ou colonne citée dans du code ou de la
   documentation doit venir d'un DDL officiel MOSIP 1.1.5 ou du catalogue PostgreSQL de l'instance (voir
   [references/mosip-115.md](references/mosip-115.md)). Si l'information manque, le dire et demander le DDL ou un
   export `pg_dump --schema-only`, plutôt que de deviner.
4. **Minimisation des données.** Capturer seulement les colonnes nécessaires aux indicateurs (`column.include.list`
   par table). Jamais de biométrie, de nom, d'adresse, de téléphone, d'e-mail, de NIU ni de texte libre dans Kafka,
   dans le Data Mart, dans les journaux ou dans les fichiers d'erreur. Le RID (clé primaire) passe en clair dans la
   clé Kafka, car Debezium ne masque pas les clés de message : topics à accès restreint, et pseudonymisation dans
   Spark avant le Data Mart. Voir [references/donnees-personnelles.md](references/donnees-personnelles.md).
5. **Aucun secret dans le dépôt.** Les exemples utilisent des variables d'environnement ou des fournisseurs de
   configuration (`${file:...}`, `${env:...}`), jamais de mot de passe réel.
6. **Un chiffre publié vient de l'état courant, jamais d'un comptage d'événements.** Une inscription change de
   statut plusieurs fois ; compter des événements CDC compte deux fois. Les agrégats sont recalculés à partir des
   tables d'état courant.

## Contexte vérifié (octobre 2026)

- **MOSIP 1.1.5** : DDL officiels au tag `v1.1.5` des dépôts MOSIP (`registration` pour `mosip_regprc`, `commons`
  pour `mosip_master`, `id-repository` pour `mosip_idrepo`, etc.). Chaque base `mosip_x` contient un schéma `x`
  (ex. `mosip_regprc` → `regprc`). Détails et colonnes relevées : [references/mosip-115.md](references/mosip-115.md).
- **Pas de table `anonymous_profile` en 1.1.5.** `idrepo.anonymous_profile` apparaît en 1.1.5.5,
  `regprc.anonymous_profile` en 1.2.0. Les indicateurs par **sexe** et **âge** n'ont donc pas de source anonyme
  en 1.1.5 : c'est une décision à faire prendre (mise à niveau, flux anonymisé dédié…), jamais un déchiffrement
  des données d'identité dans le pipeline.
- **Debezium 3.7** (stable) : `plugin.name` vaut `decoderbufs` par défaut, donc fixer `pgoutput` ; `snapshot.mode`
  n'accepte plus `never` (utiliser `no_data`) ; `skipped.operations` ignore les `TRUNCATE` par défaut ;
  `delete.handling.mode` du SMT d'aplatissement n'existe plus (remplacé par `delete.tombstone.handling.mode`).
- **Écritures dans la base MOSIP** : la table de heartbeat (`heartbeat.action.query`) et la table de signalisation
  (snapshots incrémentaux) impliquent d'écrire dans la base MOSIP, ce que la règle du dépôt interdit
  (`CLAUDE.md` : « jamais d'accès en écriture aux bases MOSIP »). Sans dérogation écrite dans `docs/decisions.md`,
  s'en passer : `snapshot.mode=initial` planifié, heartbeat sans requête, surveillance du WAL retenu.
- **EDB Postgres Advanced Server** : EDB utilise Debezium et le décodage logique dans ses propres outils, mais
  Debezium ne documente pas EPAS. Les types de compatibilité Oracle (`VARCHAR2`, `NUMBER`, `CLOB`…) et les domaines
  sont à tester en recette avant la production.
- **Spark 4.2** (stable) : mode ANSI actif par défaut ; `dropDuplicatesWithinWatermark` depuis 3.5 ; `foreachBatch`
  est « au moins une fois », l'idempotence repose sur le `batchId` et sur le Data Mart ; trigger `once` déprécié
  (utiliser `availableNow`).

Ces versions évoluent : avant d'écrire une propriété de configuration, vérifier qu'elle existe dans la version
réellement déployée (documentation officielle de cette version).

## Méthode de travail

Suivre ces étapes dans l'ordre. Ne pas sauter l'analyse : la plupart des erreurs de pipeline viennent d'une
hypothèse non vérifiée sur une table ou un statut.

### 1. Analyser le dépôt et les documents
- Lire `CLAUDE.md`, `docs/decisions.md`, `docs/indicateurs.md` (dictionnaire qui fait foi), `docs/sources-mosip.md`,
  `docs/architecture.md`, puis l'existant dans `pipeline/` et dans les migrations du Data Mart
  (`backend/src/main/resources/db/migration/`).
- Repérer les écarts avec l'architecture cible. Exemple connu : le dossier `pipeline/` contient une ébauche par lots
  (dbt + `publier.sql`) antérieure au choix du streaming ; signaler ce qui doit être remplacé et faire valider la
  décision dans `docs/decisions.md` avant de supprimer quoi que ce soit.
- Chercher les DDL disponibles (dossier convenu : `pipeline/sources/ddl/`, à créer au premier besoin). Le relevé de
  [references/mosip-115.md](references/mosip-115.md) vient des DDL officiels et suffit pour les tables et colonnes
  qu'il liste. Pour toute autre table ou colonne : lire le DDL officiel au tag de la version (lecture sur GitHub
  acceptable), puis le copier dans `pipeline/sources/ddl/` dès que du code en dépend. Pour l'instance réelle,
  proposer la requête [assets/inventaire-catalogue.sql](assets/inventaire-catalogue.sql) à faire passer par un DBA
  sur une réplique.

### 2. Inventorier les sources réelles
- Pour chaque indicateur demandé, lister les tables et colonnes MOSIP nécessaires, en citant le fichier DDL ou la
  ligne du catalogue. Classer chaque colonne : nécessaire / identifiante à pseudonymiser / interdite.
- Relever pour chaque table : clé primaire, `REPLICA IDENTITY`, volumétrie, fréquence des mises à jour, colonnes
  horodatées, valeurs distinctes des codes de statut et de type (sur une réplique ou un extrait anonymisé).
- Écrire ou compléter les fiches du dictionnaire (`docs/indicateurs.md`) : définition, calcul, dénominateur,
  règle métier, source exacte, statut « à confirmer » tant que l'équipe MOSIP n'a pas validé.

### 3. Proposer un plan, puis attendre la validation
Le plan tient sur une page : tables capturées et colonnes retenues, topics, jobs Spark, tables du Data Mart, règles
métier, tests, métriques, ce qui demande une action DBA en production, risques. Le présenter à l'humain avant
d'implémenter plusieurs composants. Une demande ciblée et explicite (« prépare la configuration du connecteur de
recette ») se traite directement : préparer un fichier non déployé n'est pas une action sur un environnement.
Lever les ambiguïtés de définition avant de coder : par exemple « par statut, chaque jour » peut vouloir dire les
inscriptions du jour réparties selon leur statut actuel (cohorte) ou le stock de dossiers par statut en fin de
journée (photo) ; voir [references/datamart.md](references/datamart.md) § 5.

### 4. Implémenter composant par composant
Dans cet ordre, chacun avec ses tests avant de passer au suivant :

| Étape | Livrable | Référence |
|---|---|---|
| Prérequis base | script DBA non destructif (rôle, publication, contrôles) | [references/debezium-postgres.md](references/debezium-postgres.md), [assets/prerequis-postgres.example.sql](assets/prerequis-postgres.example.sql) |
| Connecteur | configuration Debezium sans secret, vérifiée par le script | [assets/connecteur-debezium.example.json](assets/connecteur-debezium.example.json), `scripts/verifier_connecteur.py` |
| Sémantique CDC | règles `c`/`u`/`d`/`r`/`t`/`m` et tombstones | [references/cdc-semantique.md](references/cdc-semantique.md) |
| Streaming | job PySpark : schéma explicite, checkpoint, déduplication, erreurs | [references/spark-streaming.md](references/spark-streaming.md), [assets/job_etat_courant.example.py](assets/job_etat_courant.example.py) |
| Data Mart | état courant, registre des lots, faits recalculés, migrations additives | [references/datamart.md](references/datamart.md), [assets/datamart.example.sql](assets/datamart.example.sql) |
| Qualité | tests unitaires, intégration, rejeu, contrôles de données | [references/qualite-tests.md](references/qualite-tests.md) |
| Observabilité | métriques, seuils, requêtes de suivi | [references/observabilite.md](references/observabilite.md) |
| Exploitation | runbook, procédures d'incident | [references/exploitation.md](references/exploitation.md), [assets/runbook.template.md](assets/runbook.template.md) |

Lire la référence d'une étape au moment de la traiter, pas toutes d'avance.

### 5. Vérifier et rendre compte
Avant de rendre la main : tests au vert, `python ${CLAUDE_SKILL_DIR}/scripts/verifier_connecteur.py <fichier>` sur
chaque configuration de connecteur, et un compte rendu court : ce qui est fait, ce qui a été vérifié et comment,
ce qui reste à valider par un humain (DBA, équipe MOSIP, sécurité).

## Principes de conception

- **Un connecteur, un slot, une publication explicite.** Publication créée par le DBA avec la liste exacte des
  tables (`FOR TABLE ...`), `publication.autocreate.mode=disabled`. Pas de `FOR ALL TABLES`.
- **Clés.** La clé Kafka est la clé primaire MOSIP ; elle garantit l'ordre par ligne (même partition). Ne jamais
  repartitionner un topic CDC existant sans plan de migration.
- **Format.** Enveloppe Debezium complète (`before`, `after`, `source`, `op`) conservée jusqu'à Spark : `op` et
  `source.lsn` sont nécessaires à l'idempotence. Pas d'aplatissement par SMT qui ferait perdre ces champs.
- **État courant d'abord.** Spark écrit des tables d'état courant (une ligne par clé primaire, avec le LSN de la
  dernière modification et un indicateur de suppression). Les faits du BI sont recalculés depuis ces tables.
- **Idempotence à deux niveaux.** Garde LSN dans chaque upsert (`where excluded._lsn > cible._lsn`) et registre
  des lots traités (`pipeline.lot_traite`) dans la même transaction que les écritures. Un rejeu ne change rien.
- **Suppression logique.** Un `d` marque la ligne `_supprime = true` au lieu de l'effacer : sans la ligne, la garde
  LSN disparaît et un rejeu d'un ancien `c` la ferait revivre. La purge est un traitement séparé et validé.
- **Erreurs isolées.** Un événement illisible part dans `pipeline.evenement_rejete` avec topic, partition, offset,
  motif et empreinte, sans contenu métier. Le lot continue ; un seuil d'erreurs arrête le job.
- **Règles métier dans des tables, pas dans le code.** Le regroupement des statuts (`status_code` → statut affiché)
  vit dans une table de correspondance versionnée, validée par l'équipe MOSIP ; un code inconnu donne
  « non classé » et une alerte, jamais une valeur devinée.

## Organisation proposée dans le dépôt

```
pipeline/
  sources/ddl/            DDL MOSIP 1.1.5 de référence (copies des dépôts officiels ou pg_dump --schema-only)
  cdc/connecteurs/        configurations Debezium (*.json, sans secret) et scripts DBA (*.sql)
  streaming/              jobs PySpark (un module par domaine), configuration, tests unitaires
  datamart/               documentation des tables ; les migrations restent dans l'outil de migration du Data Mart
  tests/integration/      Kafka + PostgreSQL + Connect en conteneurs, scénarios de rejeu
docs/exploitation/        runbook, procédures d'incident, tableau des métriques
```

Si le dépôt a déjà une convention différente, la suivre et le signaler.

## Points à toujours signaler

- Une table sans clé primaire (Debezium n'émet alors que des créations sous `REPLICA IDENTITY DEFAULT`).
- Un indicateur demandé sans source dans MOSIP 1.1.5 (sexe et âge en particulier : la seule colonne `gender` de
  `regprc` est dans `individual_demographic_dedup`, à côté du nom, de la date de naissance et des coordonnées ;
  table interdite de capture).
- Une colonne sensible nécessaire à un indicateur : proposer agrégation, pseudonymisation ou dérivation à la source.
- Un écart entre le dictionnaire, le DDL et ce que le BI actuel affiche : le consigner dans `docs/decisions.md`
  (section Anomalies), sans corriger la donnée.
- Toute action qui demande un accès production : rédiger la demande pour le DBA plutôt que l'exécuter.
