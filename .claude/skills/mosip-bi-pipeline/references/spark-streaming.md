# Jobs PySpark Structured Streaming

Référence : Spark 4.2 (stable en octobre 2026). Modèle complet : [../assets/job_etat_courant.example.py](../assets/job_etat_courant.example.py).

## Sommaire
1. Découpage des jobs
2. Lecture Kafka
3. Schémas explicites et décodage
4. Déduplication
5. Écriture : `foreachBatch` idempotent
6. Checkpoints et reprise
7. Erreurs
8. Évolution des schémas
9. Réglages

## 1. Découpage des jobs

- Un job (une requête de streaming) par domaine source cohérent, par exemple « regprc → état courant ». Un job peut
  lire plusieurs topics s'ils sont toujours traités ensemble, mais ajouter un topic plus tard impose un nouveau
  checkpoint (§ 6) : prévoir dès le départ la liste.
- Le job écrit l'état courant ; les agrégats sont recalculés dans la même transaction pour les clés touchées, ou par
  un traitement SQL séparé (voir [datamart.md](datamart.md)). Pas d'agrégation en état Spark pour les indicateurs
  publiés : une inscription change de statut et un agrégat d'événements compterait deux fois.

## 2. Lecture Kafka

```python
spark.readStream.format("kafka")
  .option("kafka.bootstrap.servers", os.environ["KAFKA_BOOTSTRAP"])
  .option("subscribe", "mosip.prod.regprc.registration")   # liste explicite, pas de motif large
  .option("startingOffsets", "earliest")                   # n'agit qu'au premier démarrage (sans checkpoint)
  .option("failOnDataLoss", "true")                         # défaut ; une perte d'offsets doit arrêter le job
  .option("maxOffsetsPerTrigger", 50000)                    # borne la taille des lots
  .load()
```

- Colonnes reçues : `key`, `value` (binaires), `topic`, `partition`, `offset`, `timestamp`, `timestampType`.
  Un tombstone a `value` à `null`.
- Les options `kafka.*` sont transmises au client Kafka (sécurité SASL/SSL : depuis l'environnement, jamais en dur).
  `group.id`, `auto.offset.reset` et `enable.auto.commit` sont gérés par Spark : ne pas les fixer.
- Spark ne valide pas d'offsets dans Kafka : la position est dans le checkpoint. Le lag se lit dans les métriques de
  progression (voir [observabilite.md](observabilite.md)).

## 3. Schémas explicites et décodage

- Écrire le schéma de `after`/`before` à partir des colonnes retenues (DDL + `column.include.list`), avec les types
  produits par Debezium selon `time.precision.mode` et `decimal.handling.mode`. Jamais d'inférence de schéma.
- `from_json(value, schema)` en mode `PERMISSIVE` (défaut) : un JSON illisible donne, en Spark 4, une structure dont
  tous les champs sont nuls (constaté en test) ; le job le détecte (`value` non nul mais `op` nul) et l'envoie aux
  rejets. `DROPMALFORMED` n'est pas supporté par `from_json`.
- Spark 4 active le mode ANSI par défaut : une conversion impossible lève une erreur au lieu de renvoyer `null`.
  Convertir explicitement (horodatages en millisecondes ou microsecondes selon la configuration Debezium) et tester
  ces conversions.
- Garder `source.lsn` en `LongType`, `op` en chaîne, et ajouter `topic`, `partition`, `offset` pour la traçabilité.

## 4. Déduplication

- Dans un lot : une fenêtre par clé, ordonnée par `lsn` puis `offset` décroissants, et ne garder que la première
  ligne (`row_number() = 1`). C'est la seule déduplication nécessaire pour l'état courant, car la garde LSN du Data
  Mart rend les rejeux inoffensifs.
- Entre lots : inutile pour l'état courant (garde LSN). Pour un flux d'événements append-only (journal d'historique),
  utiliser une clé naturelle (`topic`, `partition`, `offset`) avec contrainte unique dans le Data Mart, ou
  `dropDuplicatesWithinWatermark` (Spark 3.5+, nécessite un watermark) si l'état Spark est accepté.

## 5. Écriture : `foreachBatch` idempotent

`foreachBatch` garantit « au moins une fois » : un lot peut être rejoué après un incident. Le modèle :

1. Décoder, classer (upsert / suppression / ignoré / rejet), dédupliquer par clé.
2. Ouvrir **une** transaction PostgreSQL :
   - si `(requete, lot_id)` existe déjà dans `pipeline.lot_traite` → rien à faire (lot déjà appliqué) ;
   - upserts et suppressions logiques avec garde LSN ;
   - recalcul des faits pour les clés (jour, centre…) touchées, si le recalcul est dans le job ;
   - insertion de la ligne `pipeline.lot_traite` (nombre d'événements par type) ;
   - commit.
3. En cas d'erreur : rollback, l'exception remonte, Spark rejoue le lot au redémarrage.

Le nom de requête enregistré dans `pipeline.lot_traite` contient une **génération de checkpoint** (ex.
`etat_regprc@g1`) : un nouveau checkpoint redémarre les `batchId` à 0, et sans changement de génération le registre
sauterait à tort les premiers lots.

Volume : le modèle ramène le lot sur le driver (`collect`) ; c'est adapté avec `maxOffsetsPerTrigger` borné. Pour de
gros volumes, écrire le lot dans une table de transit (`pipeline.transit_<table>`, avec `lot_id`) puis fusionner en
SQL dans la même transaction que le registre.

## 6. Checkpoints et reprise

- `checkpointLocation` sur un stockage durable et partagé (HDFS, S3 compatible, NFS), jamais en local sur un nœud
  éphémère. Un checkpoint par requête, jamais partagé.
- Ne jamais supprimer ou modifier un checkpoint à la main sans procédure validée : c'est la position de lecture.
- Changements possibles sans nouveau checkpoint : ajouter ou retirer un filtre, modifier la projection sans changer
  le schéma de sortie, changer le code de `foreachBatch`, ajouter ou retirer `maxOffsetsPerTrigger`.
- Changements qui imposent un nouveau checkpoint : changer les topics ou les sources, changer une opération avec
  état (clés d'agrégation, déduplication avec état, jointures). Procédure : nouvelle génération, relecture depuis
  `earliest` (ou depuis un snapshot incrémental), idempotence garantie par la garde LSN.
- Spark 4.2 refuse de redémarrer si le fichier de métadonnées du checkpoint manque
  (`STREAMING_CHECKPOINT_MISSING_METADATA_FILE`) : c'est le signe d'un checkpoint abîmé, pas une erreur à contourner.

## 7. Erreurs

- Événement illisible : ligne dans `pipeline.evenement_rejete` (requête, topic, partition, offset, motif, empreinte
  SHA-256 de la valeur), sans la valeur elle-même. Le contenu se retrouve si besoin dans Kafka, sous contrôle d'accès.
- Seuil : si plus de N rejets dans un lot (configurable), lever une exception : mieux vaut un pipeline arrêté et
  visible qu'un BI faux et silencieux.
- `op = t` reçu : exception immédiate (décision humaine).
- Erreurs de base (connexion, contrainte) : exception, rejeu du lot au redémarrage.
- Journaux : jamais de contenu de message ; clé seulement si elle est pseudonymisée.

## 8. Évolution des schémas

- Colonne ajoutée dans MOSIP : rien ne change tant qu'elle n'est pas dans `column.include.list`. Pour l'utiliser :
  la classer (données personnelles), l'ajouter au connecteur, au schéma Spark, à une migration additive du Data Mart,
  puis snapshot incrémental de la table si l'historique est nécessaire.
- Colonne supprimée ou renommée dans MOSIP : le schéma explicite la lit à `null`. Un contrôle qualité doit le
  détecter (taux de `null` anormal), puis adaptation validée.
- Garder un test de contrat qui compare le schéma Spark aux DDL de `pipeline/sources/ddl/`.

## 9. Réglages

- Trigger `processingTime` (ex. 1 minute) en continu ; `availableNow` pour un rattrapage ou un rejeu planifié
  (`once` est déprécié).
- État Spark (s'il y en a) : fournisseur RocksDB
  (`spark.sql.streaming.stateStore.providerClass=org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider`).
- Nommer chaque requête (`queryName`) : le nom apparaît dans les métriques et le registre des lots.
- Arrêt propre : `query.stop()` entre deux lots ; un arrêt brutal est sans danger grâce au registre et à la garde LSN.
