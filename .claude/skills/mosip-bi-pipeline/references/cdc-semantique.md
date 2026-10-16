# Sémantique des événements CDC Debezium

## Enveloppe d'un événement (valeur du message)

| Champ | Contenu |
|---|---|
| `op` | `c` création, `u` modification, `d` suppression, `r` lecture de snapshot, `t` truncate, `m` message logique |
| `before` | État avant. Sous `REPLICA IDENTITY DEFAULT` : la clé primaire seulement (pour `u` et `d`) ; `null` pour `c` et `r` |
| `after` | État après ; `null` pour `d` |
| `source` | Métadonnées : `lsn`, `txId`, `ts_ms` (heure du changement dans la base), `xmin`, `sequence` (`[dernier LSN validé, LSN courant]`), `schema`, `table`, `snapshot` |
| `ts_ms` | Heure de traitement par le connecteur. Retard CDC d'un événement = `ts_ms − source.ts_ms` |

La **clé** du message contient la clé primaire. Le **tombstone** est un message avec la même clé et une valeur
`null`, envoyé juste après un `d` (si `tombstones.on.delete=true`). Il sert à la compaction Kafka, pas à la logique
métier.

## Règles de traitement

| Cas | Traitement dans Spark → Data Mart |
|---|---|
| `c`, `r` | Upsert de `after` dans l'état courant, avec garde LSN |
| `u` | Upsert de `after`, avec garde LSN |
| `d` | Suppression logique de la clé (`_supprime = true`, `_lsn` mis à jour), avec garde LSN |
| tombstone (valeur `null`) | Ignoré (compté dans les métriques) : la suppression a déjà été traitée par le `d` |
| `t` | Ignoré par défaut (`skipped.operations=t`). S'il arrive : arrêter le job et alerter ; décision humaine |
| `m` | Ignoré sauf usage prévu |
| Message illisible (JSON invalide, champ obligatoire manquant) | `pipeline.evenement_rejete` (sans contenu métier), le lot continue ; arrêt au-delà d'un seuil |

## Clés, ordre et changement de clé primaire

- Debezium partitionne par clé : tous les événements d'une ligne vont dans la même partition, dans l'ordre de
  validation. L'ordre n'est garanti qu'à l'intérieur d'une partition.
- **Changement de clé primaire** : Debezium émet un `d` sur l'ancienne clé, un tombstone, puis un `c` sur la
  nouvelle. Les deux clés peuvent être dans des partitions différentes ; le modèle état courant + suppression
  logique le gère naturellement.
- Dans un même lot Spark, une clé peut apparaître plusieurs fois : ne garder que le dernier événement par clé
  (LSN le plus grand, puis offset) avant d'écrire.

## Garde LSN et idempotence

- Pour une même ligne, les modifications successives ont des LSN croissants (les verrous de ligne imposent l'ordre),
  ce qui permet la règle « on n'applique un événement que si son LSN est plus grand que celui déjà enregistré ».
- Un rejeu (redémarrage Spark, relecture Kafka) réapplique des événements de LSN inférieur ou égal : sans effet.
- Snapshots : les événements `r` d'un snapshot initial partagent la position du snapshot. Pour les snapshots
  incrémentaux, vérifier en recette la valeur de `source.lsn` des `r` par rapport aux modifications déjà appliquées
  (test « une ligne modifiée pendant un snapshot incrémental ») avant de choisir `>` ou `>=` dans la garde.
- Conserver `source.lsn` en entier (bigint) dans le Data Mart (`_lsn`) ; le transformer en texte fait perdre l'ordre.

## Suppressions

- Suppression logique dans l'état courant, jamais physique dans le flux : sans la ligne, la garde LSN disparaît et
  un rejeu d'un ancien `c` ferait revivre la ligne.
- Les faits du BI excluent `_supprime = true`. Une suppression MOSIP fait donc baisser un compteur : c'est voulu, et
  le dictionnaire doit le dire (une inscription supprimée n'est plus comptée).
- Purge des lignes supprimées : traitement séparé, après une durée supérieure à la rétention Kafka (aucun rejeu ne
  peut plus les ramener), validé par un humain.
