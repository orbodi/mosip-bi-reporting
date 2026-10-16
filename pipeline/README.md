# Pipeline de données

Les bases MOSIP sont lues par **capture des changements** (décision du 16/10/2026, `docs/decisions.md`) :

```
MOSIP regprc.registration ─ Debezium ─▶ Kafka ─▶ job PySpark ─▶ etat.registration ─▶ bi.fait_enrolement_jour ─▶ API ─▶ page
   (slot logique, publication)    (topic mosip.<env>.regprc.registration)   (empreinte HMAC, garde LSN)   (recalcul par case)
```

Guide de conception et d'exploitation : skill `/mosip-bi-pipeline` (`.claude/skills/mosip-bi-pipeline/`).

| Dossier | Contenu |
|---|---|
| `sources/ddl/` | DDL officiels MOSIP v1.1.5 copiés sans modification (source et date en tête de fichier) |
| `cdc/connecteurs/` | Configurations Debezium sans secret (`regprc-dev.json` pour l'environnement local) |
| `streaming/enrolement/` | Job temps réel de l'enrôlement ; tests dans `streaming/tests/` (vrai PostgreSQL, vraies migrations) |
| `simulateur/` | Simulateur d'activité MOSIP pour le développement (inscriptions fictives) |
| `outils/` | Enregistrement du connecteur, vérification de bout en bout |
| `Dockerfile` | Image de développement (Python 3.12, Java 17, PySpark 4.2, connecteur Kafka de Spark) |
| `journaux/` | Scripts des journaux ABIS et IDPS (hors MOSIP) |
| `models/`, `extraction/`, `tests/`, `publier.sql`, `dbt_project.yml` | Ébauche par lots antérieure (dbt) : ne pas l'étendre, ne plus lancer `publier.sql` (il écraserait les faits du pipeline) |

Les tables du Data Mart (`etat`, `pipeline`, colonnes de `bi`) sont créées par la migration Flyway
`backend/src/main/resources/db/migration/V2__pipeline_temps_reel_enrolement.sql`, appliquée par l'API au démarrage.

## Environnement local temps réel (Docker Desktop)

Prérequis : Docker Desktop avec au moins 8 Go de mémoire attribués, accès Internet au premier lancement (images,
dépendances Maven et npm, connecteur Kafka de Spark). Ports utilisés : 5173, 8080, 8083, 8090, 5432, 5433.

```powershell
# depuis la racine du dépôt
docker compose -f deploy/docker-compose.yml --profile temps-reel up -d --build
```

Le premier lancement prend 5 à 15 minutes (construction de l'image du pipeline, téléchargement des dépendances de
l'API). Ensuite : http://localhost:5173/enrolement. Le bloc « Devenir des inscriptions » se met à jour seul toutes les
30 secondes ; la pastille « Dernière mise à jour » suit le dernier changement reçu.

| Service | Rôle |
|---|---|
| `mosip-sim` | PostgreSQL « MOSIP » simulé : table `regprc.registration` au DDL officiel, rôle `bi_cdc`, publication `bi_cdc_regprc`, TLS, `wal_level=logical` |
| `simulateur-mosip` | crée 3 000 inscriptions fictives sur 60 jours, puis 1 à 4 nouvelles toutes les 5 s, et fait avancer celles en cours |
| `kafka` | Apache Kafka 4.1.1 (un nœud, KRaft) |
| `kafka-ui` | interface web de Kafka (Kafbat UI 1.5.0) sur http://localhost:8090 : topics, messages, retard des consommateurs, état du connecteur Debezium ; lecture seule, accessible depuis le poste seulement |
| `connect` | Kafka Connect avec Debezium 3.7.0 ; secrets lus dans son environnement (`${env:...}`) |
| `connect-init` | enregistre `cdc/connecteurs/regprc-dev.json` puis s'arrête (attend l'état RUNNING) |
| `spark-enrolement` | job PySpark, un lot toutes les 10 s, checkpoint dans le volume `checkpoints-spark` |
| `api` | API Spring Boot (profil dev : migrations, centres et correspondance des statuts de démonstration) |
| `front` | interface Vite sur le port 5173, appels `/api` vers le service `api` |

### Vérifier la chaîne

```powershell
docker compose -f deploy/docker-compose.yml run --rm outils
```

Compte rendu par étape (base simulée, slot, connecteur, lots Spark, rejets, concordance état courant ↔ faits,
fraîcheur, API). Tout doit être « OK » ; « ALERTE » sur `enrolement_non_classees` signale des statuts sans
correspondance validée. Suivre un service : `docker compose -f deploy/docker-compose.yml logs -f spark-enrolement`.

Dans l'interface Kafka (http://localhost:8090) : le topic `mosip.dev.regprc.registration` reçoit un message par
changement dans MOSIP (clé = RID, valeur = enveloppe Debezium `before` / `after` / `source` / `op`) ; l'onglet
Consumers montre le retard de lecture du job Spark ; l'onglet Kafka Connect montre l'état du connecteur
`bi-cdc-regprc-dev`. L'interface est en lecture seule : pour redémarrer le connecteur, passer par l'API REST de
Kafka Connect (port 8083).

Délai attendu entre un changement dans MOSIP et l'écran : quelques secondes pour Debezium, au plus 10 s pour le lot
Spark, au plus 30 s pour la relecture de la page.

### Arrêter, repartir de zéro

```powershell
docker compose -f deploy/docker-compose.yml --profile temps-reel stop              # arrêt, données conservées
docker compose -f deploy/docker-compose.yml --profile temps-reel down              # supprime les conteneurs
docker compose -f deploy/docker-compose.yml --profile temps-reel down -v           # ET les volumes : tout est effacé
```

`down -v` efface aussi la base BI locale (volume `donnees-bi`). Ne pas supprimer un volume seul :
- Kafka effacé, checkpoint conservé : le job s'arrête (offsets disparus, `failOnDataLoss`), ce qui est voulu ;
- checkpoint effacé, Data Mart conservé : le job refuse de démarrer ; changer de génération dans
  `deploy/docker-compose.yml` (`NOM_REQUETE: etat_regprc@g2`, `CHECKPOINT_LOCATION: .../etat_regprc_g2`). La nouvelle
  génération relit tout le topic sans double comptage (garde LSN).

### Tests

```powershell
docker compose -f deploy/docker-compose.yml up -d postgres
docker compose -f deploy/docker-compose.yml run --rm outils python -m pytest
```

Ou en local (Python 3.11+, Java 17+) : `pip install -r pipeline/requirements.txt`, puis `cd pipeline` et
`python -m pytest` (variable `DATAMART_DSN_TEST`, par défaut `host=localhost user=bi dbname=postgres`). Les tests
créent la base `bi_test_pipeline` et y appliquent les vraies migrations du backend.

Ce qu'ils couvrent : décodage des événements Debezium (`c`, `r`, `u`, `d`, tombstone, `t`, `m`, messages illisibles),
dernier événement par clé, lot rejoué, nouvelle génération de checkpoint, événement ancien, suppression puis rejeu,
changement de statut, TRUNCATE, seuil de rejets, absence du RID dans le Data Mart, reprise du streaming sur
checkpoint, format des RID simulés.

## Règles appliquées (à confirmer avec l'équipe MOSIP, voir `docs/decisions.md`)

- Jour d'une inscription : `cr_dtimes` (réception par MOSIP), règle provisoire du 16/10/2026.
- Exclues des faits : inscriptions supprimées dans MOSIP (événement `d`) et `is_deleted = true`.
- Statut affiché : `pipeline.correspondance_statut` ; un code absent compte en « non classées ». La correspondance
  chargée en développement (`db/dev/R__donnees_dev.sql`) est une démonstration, jamais chargée ailleurs.
- Centre : 5 premiers chiffres du RID ; un code absent de `bi.zone` compte sous « Centre non référencé ».
- Sexe et âge : « inconnu » (pas de source anonymisée en MOSIP 1.1.5).

## Passer en recette (MOSIP réelle) : ce qui change

Rien ne s'exécute sur une base MOSIP sans validation de l'action précise par le DBA ou l'exploitation.

1. Prérequis base par le DBA : `wal_level=logical`, `max_slot_wal_keep_size`, rôle `REPLICATION` sans superutilisateur,
   `SELECT` sur `regprc.registration` seulement, publication explicite, ligne `pg_hba.conf` (skill, fichier
   `assets/prerequis-postgres.example.sql`). Les scripts de `deploy/mosip-sim/init` ne s'appliquent qu'à la simulation.
2. Connecteur `cdc/connecteurs/regprc-recette.json` à créer depuis `regprc-dev.json` : nom, slot et préfixe de topic
   de l'environnement, hôte réel, `sslmode=verify-full` si possible, secrets par `${file:...}` ; le contrôler avec
   `python .claude/skills/mosip-bi-pipeline/scripts/verifier_connecteur.py <fichier>`.
3. Pas de simulateur. Clé HMAC propre à l'environnement, dans le coffre de secrets. ACL Kafka : topics lisibles par le
   seul pipeline (le RID y passe en clair).
4. Correspondance des statuts validée par l'équipe MOSIP, chargée par une migration ou une procédure tracée.
5. Kafka, Kafka Connect et Spark fournis par l'exploitation (à préciser) ; runbook à partir du modèle du skill.

## Ébauche par lots (antérieure, dbt)

```
MOSIP (lecture seule) ──extraction/──▶ schéma brut ──dbt──▶ schéma bi_calc ──publier.sql──▶ schéma bi
```

Conservée jusqu'à la décision de retrait (`docs/decisions.md`, point 7 de « À trancher pour le pipeline CDC »).
