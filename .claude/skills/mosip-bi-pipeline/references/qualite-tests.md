# Tests et contrôles qualité

## Tests unitaires (sans infrastructure)

Sur les fonctions pures du job (à isoler du code d'E/S) :
- décodage de l'enveloppe : `c`, `u`, `d`, `r` ; tombstone ; JSON invalide ; champ obligatoire manquant ;
- classement des événements (upsert, suppression, ignoré, rejet, arrêt sur `t`) ;
- déduplication par clé dans un lot (dernier LSN, puis offset) ;
- dérivations (centre et machine depuis le RID, jour depuis l'horodatage, empreinte HMAC) ;
- correspondance des statuts (code inconnu → `non_classe`) ;
- conversions de types selon `time.precision.mode` / `decimal.handling.mode`.

Outils : `pytest` et une session Spark locale (`local[2]`) pour les fonctions DataFrame ; jeux d'événements JSON
synthétiques dans `pipeline/streaming/tests/donnees/` (aucune donnée réelle).

## Tests d'intégration (conteneurs)

Pile : PostgreSQL (image de la version d'EPAS ou PostgreSQL de même version majeure, `wal_level=logical`), Kafka,
Kafka Connect avec Debezium, Data Mart PostgreSQL, job Spark en local. Testcontainers ou Docker Compose dédié aux
tests.

Scénarios obligatoires :
1. **Bout en bout** : insertion, modifications de statut, suppression dans une table source au schéma copié du DDL
   MOSIP → état courant et faits attendus.
2. **Rejeu** : rejouer les mêmes offsets (nouvelle génération de checkpoint lisant depuis `earliest`) → Data Mart
   identique, octet pour octet sur les faits.
3. **Arrêt brutal** : tuer le job pendant l'écriture d'un lot, redémarrer → aucun double comptage, registre cohérent.
4. **Lot rejoué** : appeler la fonction d'écriture deux fois avec le même `batchId` → la seconde est sans effet.
5. **Désordre** : un `u` ancien relu après un `u` récent → ignoré (garde LSN).
6. **Suppression puis rejeu du `c`** : la ligne reste supprimée.
7. **Changement de clé primaire** : `d` + tombstone + `c` → une ligne supprimée, une créée.
8. **Message illisible** : rejet tracé sans contenu, le lot continue ; seuil d'arrêt respecté.
9. **Snapshot incrémental** pendant des modifications : état final correct (choix de `>` ou `>=` dans la garde).
10. **Heartbeat** : base calme, slot qui avance.

## Contrôles qualité des données (en production)

Exécutés après chaque lot (contrôles légers) ou périodiquement (contrôles lourds), résultats dans
`pipeline.controle_qualite` :

| Contrôle | Règle |
|---|---|
| Égalité des statuts | somme des statuts regroupés = total des inscriptions, par case de fait |
| Conservation | inscriptions de l'état courant (non supprimées) = total des faits |
| Centres | part des inscriptions dont le centre est absent du référentiel < seuil |
| Codes | aucun code de statut ou de type non classé (sinon alerte) |
| Réconciliation source | comptages par jour et statut sur une réplique MOSIP (lecture seule, hors heures de pointe) = état courant, à tolérance près du retard |
| Nulls | taux de `null` par colonne retenue stable (détecte une colonne supprimée ou renommée côté MOSIP) |
| Fraîcheur | `dernier_chargement` récent ; `derniere_donnee` cohérente avec l'activité attendue |
| Valeurs de référence | chiffres connus du dictionnaire (`docs/indicateurs.md`) retrouvés sur l'instantané correspondant |

Un contrôle en échec n'altère pas les données : il alerte, s'affiche dans la supervision et, pour les contrôles
bloquants, suspend la mise à jour de `bi.source_fraicheur` (le BI montre alors des données plus anciennes mais
justes).

## Intégration continue

- Unitaires et contrat de schéma (schéma Spark ↔ DDL de `pipeline/sources/ddl/`) à chaque pull request.
- `scripts/verifier_connecteur.py` sur chaque fichier de connecteur.
- Intégration en conteneurs au moins chaque nuit et avant chaque mise en production.
