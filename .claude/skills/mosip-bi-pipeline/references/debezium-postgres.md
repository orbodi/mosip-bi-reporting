# Debezium sur EDB PostgreSQL : prérequis, connecteur, slots et WAL

Référence : documentation Debezium 3.7 (stable en octobre 2026), connecteur PostgreSQL. Vérifier chaque propriété
dans la documentation de la version réellement déployée.

## Sommaire
1. Prérequis côté base (DBA)
2. Rôle et privilèges
3. Publication et `REPLICA IDENTITY`
4. Slot logique et rétention du WAL
5. Snapshots
6. Configuration du connecteur
7. Format des messages et topics
8. EDB Postgres Advanced Server : points à tester

## 1. Prérequis côté base (DBA)

| Paramètre | Valeur | Remarque |
|---|---|---|
| `wal_level` | `logical` | Redémarrage de l'instance nécessaire : action de production, validation explicite |
| `max_replication_slots` | ≥ nombre de connecteurs + marge | Défaut PostgreSQL : 10 |
| `max_wal_senders` | ≥ nombre de connecteurs + réplications existantes | Défaut : 10 |
| `max_slot_wal_keep_size` | valeur bornée (ex. quelques dizaines de Go, selon le disque) | PG13+. Défaut `-1` = illimité : un slot arrêté peut remplir le disque |
| `pg_hba.conf` | ligne pour **la base** (ex. `mosip_regprc`), le rôle Debezium et l'hôte Kafka Connect | Le mot-clé `replication` de `pg_hba.conf` ne couvre que la réplication physique ; une connexion de réplication logique est filtrée par le nom de la base |

Le script [../assets/prerequis-postgres.example.sql](../assets/prerequis-postgres.example.sql) contient les
contrôles (lecture) et les commandes (commentées) à faire passer par le DBA.

## 2. Rôle et privilèges

- Rôle dédié : `CREATE ROLE <role_debezium> REPLICATION LOGIN` ; mot de passe géré hors dépôt.
- Droit `CREATE` sur la base : nécessaire seulement si Debezium crée lui-même la publication. Avec une publication
  créée par le DBA (`publication.autocreate.mode=disabled`), ne pas l'accorder ; confirmer en recette que le
  connecteur démarre sans.
- `SELECT` uniquement sur les tables capturées (le snapshot les lit).
- Pas de superutilisateur. Aucune écriture dans la base MOSIP par défaut (règle du dépôt). Les tables de heartbeat et
  de signalisation (§ 4 et § 5) en demandent : seulement après une dérogation écrite dans `docs/decisions.md`.

## 3. Publication et `REPLICA IDENTITY`

- Créer la publication à la main, avec la liste exacte des tables : `CREATE PUBLICATION <pub> FOR TABLE s.t1, s.t2;`
  Cela demande `CREATE` sur la base et la propriété des tables : c'est au DBA (ou au propriétaire du schéma MOSIP)
  de le faire. `FOR ALL TABLES` et `FOR TABLES IN SCHEMA` exigent un superutilisateur : à éviter.
- Côté connecteur : `publication.name=<pub>` et `publication.autocreate.mode=disabled`.
- Ajouter une table plus tard : `ALTER PUBLICATION <pub> ADD TABLE ...` (DBA), puis ajouter la table à
  `table.include.list`, puis lancer un snapshot incrémental de cette seule table.
- `REPLICA IDENTITY` détermine le contenu de `before` :
  - `DEFAULT` (clé primaire) : `before` ne contient que la clé. Suffisant pour notre modèle (état courant + LSN).
  - `FULL` : toutes les colonnes ; coûte du WAL en plus. À réserver aux tables sans clé primaire, après accord DBA.
  - Une table sans clé primaire ni identité ne peut pas publier ses `UPDATE`/`DELETE` : la signaler.
- Ne pas modifier `REPLICA IDENTITY` d'une table MOSIP sans validation : c'est une modification du schéma de production.

## 4. Slot logique et rétention du WAL

Un slot retient le WAL tant que Debezium n'a pas confirmé sa position. Connecteur arrêté = WAL qui grossit.

- Un slot par connecteur (`slot.name`, minuscules, chiffres et `_`), nommé avec l'environnement :
  `bi_cdc_regprc_prod`.
- `slot.drop.on.stop=false` (défaut) : ne jamais supprimer un slot automatiquement en production.
- **Heartbeat** : `heartbeat.interval.ms` (ex. 60000) fait émettre des messages de vie par le connecteur. Quand les
  tables capturées sont calmes alors que le reste de la base écrit du WAL, le slot peut ne pas avancer ; la parade
  documentée est `heartbeat.action.query`, qui écrit dans une petite table technique publiée (ex.
  `bi_cdc.heartbeat`). C'est une écriture dans la base MOSIP : dérogation écrite obligatoire. Sans dérogation :
  heartbeat sans requête, surveillance du WAL retenu et seuil d'alerte prudent (voir
  [observabilite.md](observabilite.md)).
- Surveiller (voir [observabilite.md](observabilite.md)) : `pg_replication_slots.active`, `wal_status`
  (`reserved`, `extended`, `unreserved`, `lost`), `safe_wal_size`, et le WAL retenu
  `pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)`.
- `wal_status = lost` : le slot ne peut plus reprendre ; il faut un nouveau slot et un nouveau snapshot (procédure
  dans [exploitation.md](exploitation.md), validation obligatoire).
- Supprimer un slot (`pg_drop_replication_slot`) est une action de production : validation explicite, et
  uniquement après avoir arrêté le connecteur et prévu la reprise.

## 5. Snapshots

`snapshot.mode` (3.7) : `initial` (défaut), `always`, `initial_only`, `no_data`, `when_needed`,
`configuration_based`, `custom`. `never` n'existe plus.

- Premier démarrage : `initial` lit les tables puis enchaîne sur le flux. Sur de grosses tables MOSIP (millions de
  lignes), prévoir la fenêtre (hors heures de pointe), la charge et la rétention Kafka.
- `no_data` seul ne charge **jamais** les lignes déjà présentes : l'état courant ne contiendrait que les
  inscriptions modifiées après le démarrage, et tous les indicateurs seraient faux. `no_data` ne se justifie qu'avec
  un snapshot incrémental planifié juste après.
- **Snapshot incrémental** (utile pour les reprises et les ajouts de tables, sans relire tout) : il demande une table de
  signalisation dans la base source, donc une écriture dans la base MOSIP et une dérogation écrite. Sans elle :
  `initial` au premier démarrage, et pour une reprise, nouveau connecteur (nouveau slot) en `initial`, validé.
  Mise en place quand la dérogation existe : table de signalisation
  `signal.data.collection=<schema>.<table>` (colonnes `id` VARCHAR clé, `type` VARCHAR, `data` VARCHAR), incluse
  dans la publication ; insertion d'une ligne `type='execute-snapshot'`,
  `data='{"data-collections":["regprc.registration"],"type":"incremental"}'`. Créer cette table dans un schéma
  technique (ex. `bi_cdc`), jamais dans un schéma MOSIP, et faire valider son ajout.
- `always` relit tout à chaque redémarrage : à éviter.
- Les événements de snapshot ont `op = r` : ils sont traités comme des créations (voir
  [cdc-semantique.md](cdc-semantique.md)).

## 6. Configuration du connecteur

Modèle : [../assets/connecteur-debezium.example.json](../assets/connecteur-debezium.example.json). Points clés :

| Propriété | Valeur conseillée | Pourquoi |
|---|---|---|
| `plugin.name` | `pgoutput` | Le défaut est `decoderbufs`, qui demande un module serveur |
| `topic.prefix` | `mosip.<env>` | Préfixe des topics ; ne jamais le changer ensuite (nouveaux topics) |
| `table.include.list` | liste explicite `regprc.registration,...` | Pas de capture par défaut de tout un schéma |
| `column.include.list` | colonnes « nécessaires » + clés | Minimisation à la source (ne pas combiner avec `column.exclude.list`) |
| `column.mask.hash.v2.SHA-256.with.salt.<sel>` | colonnes identifiantes **hors clé primaire** à pseudonymiser | Empreinte stable ; v2 conseillée ; colonnes texte seulement ; le sel est un secret. **Ne masque pas la clé du message** : la clé primaire (RID) part en clair dans la clé Kafka, à pseudonymiser dans Spark (voir [donnees-personnelles.md](donnees-personnelles.md)) |
| `publication.autocreate.mode` | `disabled` | Publication gérée par le DBA |
| `snapshot.mode` | `initial` (ou `no_data` suivi d'un snapshot incrémental, si dérogation) | Voir § 5 : `no_data` seul ne charge pas l'existant |
| `tombstones.on.delete` | `true` | Compaction Kafka possible ; Spark sait les ignorer |
| `skipped.operations` | `t` (défaut) | Un `TRUNCATE` MOSIP est exceptionnel : à traiter à la main |
| `decimal.handling.mode` | `string` ou `precise` | Pas de `double` pour des montants ou identifiants numériques |
| `time.precision.mode` | `adaptive` (défaut) ou `connect` | Choisir une fois, déclarer le schéma Spark en conséquence |
| `heartbeat.interval.ms` / `heartbeat.action.query` | intervalle toujours ; requête seulement avec dérogation | Avancement du slot (§ 4) |
| `provide.transaction.metadata` | `false` sauf besoin | Topic supplémentaire |
| `lsn.flush.mode` | `connector` (défaut) | `flush.lsn.source` est déprécié |
| secrets | `${file:/chemin/secrets.properties:cle}` ou `${env:VARIABLE}` | Jamais de mot de passe en clair. Demande `config.providers=file,env` (et les classes `FileConfigProvider` / `EnvVarConfigProvider`) dans la configuration du worker Kafka Connect |
| `errors.log.include.messages` | `false` | Les messages contiennent des identifiants : pas dans les journaux |
| `database.sslmode` | `require` au minimum, `verify-full` si possible | Flux chiffré entre la base et Kafka Connect |

`scripts/verifier_connecteur.py` contrôle les règles de ce tableau sur un fichier de configuration.

## 7. Format des messages et topics

- Convertisseur : JSON sans schéma embarqué (`value.converter.schemas.enable=false`) pour démarrer, ou Avro / JSON
  Schema avec un registre de schémas si l'équipe en exploite un. Le choix fixe la façon dont Spark lit les messages.
- Topics nommés `<topic.prefix>.<schema>.<table>`. Créés à l'avance par l'équipe Kafka avec : nombre de partitions
  (définitif, voir clés), facteur de réplication ≥ 3, rétention suffisante pour une reprise Spark (au moins plusieurs
  jours), `cleanup.policy=compact,delete` seulement si l'on accepte de perdre l'historique des changements.
- Pas de SMT d'aplatissement (`ExtractNewRecordState`) : Spark a besoin de `op`, `before` et `source.lsn`.

## 8. EDB Postgres Advanced Server : points à tester

Debezium ne documente pas EPAS. EDB utilise lui-même Debezium et le décodage logique (EPAS 12 à 18) dans ses outils,
ce qui est encourageant mais ne vaut pas validation. En recette, avant la production :
- `select version();` et confirmer que `pgoutput` fonctionne (création du slot, flux d'un `UPDATE`).
- Tables capturées utilisant des types de compatibilité Oracle (`VARCHAR2`, `NUMBER`, `DATE` à la manière
  d'Oracle, `CLOB`, `BLOB`) ou des domaines : vérifier le type émis. Debezium ignore une colonne de type inconnu
  (avec un avertissement) sauf `include.unknown.datatypes=true`.
- Objets volumineux (large objects) : non capturés par le décodage logique.
- Décodage logique sur un serveur de secours (fonction PostgreSQL 16 et plus, documentée pour EPAS 18, avec
  `hot_standby_feedback`) : réduit la charge sur le primaire, mais à valider avec le DBA pour la version installée.
