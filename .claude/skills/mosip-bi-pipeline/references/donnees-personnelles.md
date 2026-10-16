# Données personnelles et biométriques MOSIP

MOSIP est le registre d'identité nationale : les données traitées relèvent de la protection des données personnelles
du Togo et de la politique de sécurité de l'ANID. Le pipeline ne doit transporter que ce qu'un indicateur agrégé exige.

## Principes

1. **Minimisation à la source.** La sélection se fait dans Debezium (`table.include.list`, `column.include.list`),
   pas plus loin : ce qui n'entre pas dans Kafka ne peut pas fuir de Kafka, de Spark, des checkpoints ni des journaux.
2. **Jamais transportés ni stockés** : biométrie et références biométriques en clair, nom, prénom, date de naissance
   exacte, adresse, téléphone, e-mail, NIU, numéro de document, photo, textes libres (`req_text`, `resp_text`,
   `res_text`, `status_comment`, `remarks`, `additional_info`…), contenus de paquets, `uin_data`.
3. **Identifiants techniques** (RID, `bio_ref_id`, identifiant d'agent) : dériver les attributs utiles (centre,
   machine, date) puis pseudonymiser avant le Data Mart.
   - **La clé du message Kafka n'est pas masquée par Debezium** : `column.mask.hash.*` et `column.mask.with.*`
     ne s'appliquent qu'à la valeur (`before`/`after`), la clé primaire part en clair dans la clé du message
     (vérifié dans le code de Debezium 3.7). Le RID transite donc par Kafka : topics CDC à accès restreint (ACL),
     rétention limitée.
   - Pseudonymisation dans Spark, avant toute écriture : HMAC-SHA-256 avec une clé secrète (différente par
     environnement, conservée hors dépôt). Le Data Mart ne reçoit que l'empreinte et les attributs dérivés.
   - `column.mask.hash.v2.SHA-256.with.salt.<sel>` reste utile pour des colonnes identifiantes **hors clé** dont on
     n'a pas besoin en clair.
   - `message.key.columns` permet de changer la clé, mais impose `REPLICA IDENTITY FULL` si la colonne n'est pas la
     clé primaire, et la nouvelle clé n'est pas masquée non plus : rarement une bonne option.
4. **Pas de déchiffrement.** Le pipeline ne déchiffre aucune donnée MOSIP. Un indicateur qui l'exigerait est
   remonté comme décision (voir sexe et âge en 1.1.5).
5. **Agrégats publiés** : seuil de diffusion pour les petites cellules (ex. moins de 5 inscriptions pour un centre,
   un jour et une tranche d'âge) à décider avec la sécurité, appliqué par l'API.

## Environnements de test

- Jamais de copie de production en développement ou en recette sans masquage validé.
- Données de test : générateur synthétique (RID fictifs au bon format, centres du référentiel, statuts réels) dans
  `pipeline/tests/donnees/`. Aucune donnée réelle dans le dépôt, même anonymisée, sans validation.
- Si une recette sur données réelles est exigée : réplique masquée par le DBA, accès nominatif, durée limitée,
  journalisée.

## Contrôle des accès

| Composant | Accès |
|---|---|
| Rôle Debezium | `REPLICATION`, `SELECT` sur les tables capturées, rien d'autre |
| Topics Kafka CDC | ACL : écriture par Kafka Connect, lecture par le compte du job Spark ; aucun accès humain par défaut |
| Checkpoints Spark | Stockage chiffré, accès limité au compte du job (ils peuvent contenir des données d'état) |
| Data Mart `etat`, `pipeline` | Rôle du pipeline ; audit en lecture |
| Data Mart `bi` | API en lecture seule ; utilisateurs via l'API et sa portée géographique |
| Secrets | Coffre ou fichiers protégés montés au démarrage ; jamais dans les configurations versionnées |

## Journaux et erreurs

- Jamais de contenu de message dans les journaux, les rejets ou les exceptions remontées.
- Rejets : coordonnées Kafka + motif + empreinte, pas de valeur.
- Rétention des topics CDC alignée sur le besoin de reprise, pas plus.

## Revue

Toute modification de `column.include.list`, d'un schéma Spark ou d'une table du Data Mart qui ajoute une colonne
passe par la classification ([mosip-115.md](mosip-115.md) § 5) et une revue (agent `relecteur-securite` du dépôt).
