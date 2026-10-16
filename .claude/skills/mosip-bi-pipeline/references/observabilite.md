# Observabilité du pipeline

Chaque maillon expose son retard ; une alerte doit dire où regarder. Seuils indicatifs, à ajuster après deux
semaines de mesure en recette.

## Tableau des métriques

| Maillon | Métrique | Source | Seuil d'alerte indicatif |
|---|---|---|---|
| PostgreSQL | WAL retenu par slot (octets) | `pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)` | > 50 % de `max_slot_wal_keep_size` ou de l'espace libre |
| PostgreSQL | État du slot | `pg_replication_slots.active`, `wal_status`, `safe_wal_size` | inactif > 15 min ; `wal_status` = `unreserved` ; `lost` = incident majeur |
| PostgreSQL | Retard de confirmation | `pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)` | croissance continue sur 30 min |
| PostgreSQL (14+) | Débordements du décodage | `pg_stat_replication_slots` (`spill_txns`, `spill_bytes`, `total_txns`) | croissance anormale des `spill_*` |
| Debezium | Retard CDC | JMX `debezium.postgres:type=connector-metrics,context=streaming,server=<topic.prefix>` : `MilliSecondsBehindSource` | > 5 min |
| Debezium | Silence | `MilliSecondsSinceLastEvent`, `Connected` | `Connected` = false ; silence > 2 × intervalle de heartbeat |
| Debezium | File interne | `QueueRemainingCapacity`, `CurrentQueueSizeInBytes` | capacité restante < 10 % |
| Debezium | Volumes | `TotalNumberOfCreateEventsSeen`, `...UpdateEventsSeen`, `...DeleteEventsSeen`, `NumberOfErroneousEvents` | erreurs > 0 |
| Kafka Connect | État du connecteur et des tâches | API REST `GET /connectors/<nom>/status` | état ≠ `RUNNING` |
| Kafka | Lag de lecture Spark | Progression Spark : `sources[].metrics.maxOffsetsBehindLatest`, `avgOffsetsBehindLatest` | croissance continue ; > 1 lot max |
| Spark | Progression | `StreamingQueryProgress` : `batchId`, `numInputRows`, `inputRowsPerSecond`, `processedRowsPerSecond`, `durationMs.triggerExecution` | traitement < entrée pendant 15 min ; durée de lot > intervalle de trigger |
| Spark | Requête vivante | `StreamingQueryListener` (`onQueryProgress`, `onQueryIdle`, `onQueryTerminated`) | terminaison ; pas de progression ni d'inactivité signalée depuis 10 min |
| Pipeline | Rejets | `pipeline.evenement_rejete` par requête et par heure | > 0 en continu ; seuil d'arrêt atteint |
| Pipeline | Lots | `pipeline.lot_traite` : dernier `traite_le`, volumes | aucun lot depuis 15 min alors que Debezium émet |
| Data Mart | Fraîcheur BI | `bi.source_fraicheur.derniere_donnee` et `dernier_chargement` | `now() - dernier_chargement` > 30 min |
| Data Mart | Contrôles qualité | `pipeline.controle_qualite` : dernier statut par contrôle | statut en échec |

Le retard de bout en bout se décompose : `MilliSecondsBehindSource` (base → Kafka) + lag Spark (Kafka → lot) + durée
du lot (lot → Data Mart). La pastille du BI montre `derniere_donnee` : distinguer « la source n'a rien produit »
(MOSIP arrêté, comme mi-janvier 2026) de « le pipeline est en retard ».

## Requêtes de suivi

```sql
-- Slots : état et WAL retenu (lecture, sur le primaire)
select slot_name, active, wal_status, safe_wal_size,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn))        as wal_retenu,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) as retard_confirmation
from pg_replication_slots
where slot_type = 'logical';

-- Fraîcheur du BI
select source, derniere_donnee, dernier_chargement, now() - dernier_chargement as depuis_chargement
from bi.source_fraicheur order by ordre;

-- Activité du pipeline sur 24 h
select requete, count(*) as lots, sum(nb_upserts) as upserts, sum(nb_suppressions) as suppressions,
       sum(nb_rejets) as rejets, max(traite_le) as dernier_lot
from pipeline.lot_traite where traite_le > now() - interval '24 hours' group by requete;
```

`pg_current_wal_lsn()` ne s'exécute pas sur un serveur de secours ; sur un secours, utiliser
`pg_last_wal_replay_lsn()`.

## Collecte

- Spark : un `StreamingQueryListener` qui écrit chaque progression en JSON (sans données) dans les journaux, et
  publie les métriques vers l'outil de supervision en place.
- Debezium : exporteur JMX (Prometheus ou équivalent) sur Kafka Connect.
- PostgreSQL : requêtes ci-dessus via l'exporteur ou l'outil de supervision de la base, avec un rôle de supervision
  en lecture (`pg_monitor`).
- Tableau de bord unique : une ligne par maillon, du slot à la fraîcheur BI, avec les seuils ci-dessus.
