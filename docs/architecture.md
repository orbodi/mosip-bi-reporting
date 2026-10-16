# Architecture

```
 MOSIP (EDB PostgreSQL, aucune écriture)            Journaux ABIS (BRS, MBSS), IDPS
        │ réplication logique (slot, publication)     │
        ▼                                             │
 Debezium (Kafka Connect)                             │
        ▼                                             │
 Kafka (un topic par table capturée)                  │
        ▼                                             ▼
 PySpark Structured Streaming                       scripts (pipeline/journaux/)
        └─────────────────────┬───────────────────────┘
                              ▼
   Data Mart PostgreSQL : schémas « etat », « pipeline », « bi »
                              │ l'API ne lit que « bi »
                              ▼
   backend/ API Spring Boot (/api/v1/…, OpenAPI), jeton Keycloak vérifié, zone appliquée
                              ▼
   frontend/ React (SPA), connexion Keycloak (PKCE)
```

## Data Mart PostgreSQL
- `etat` : état courant des tables MOSIP capturées (colonnes retenues, RID remplacé par son empreinte HMAC, LSN du
  dernier événement appliqué, suppression logique). Lu par le pipeline seulement.
- `pipeline` : registre des lots traités (idempotence), événements rejetés (sans leur contenu), contrôles qualité,
  correspondance des statuts MOSIP.
- `bi` : tables lues par l'API (ci-dessous).

## Schéma `bi`
- `zone` : arborescence du territoire (niveau, code, nom, parent) de la région au centre.
- `source_fraicheur` : dernière donnée et dernier chargement par source.
- Tables de faits agrégées au jour, une par domaine (`fait_enrolement_jour`, `fait_carte_jour`, `fait_abis_jour`,
  `fait_idps_jour`, `fait_authentification_jour`), au grain le plus fin utile (centre × jour × sexe × tranche × type ;
  sexe et tranche à « inconnu » tant que leur source n'est pas décidée).
  Les pages et l'Exploration lisent les mêmes tables : les chiffres concordent par construction.
- Stocks (en attente, ancienneté) dans des tables d'instantané datées.
- Migrations Flyway dans `backend/src/main/resources/db/migration` ; le pipeline écrit, l'API lit (deux rôles PostgreSQL).
  Les schémas `etat` et `pipeline` arrivent par de nouvelles migrations, sans modifier celles déjà appliquées.

## Pipeline CDC (bases MOSIP)
- Un connecteur Debezium, un slot logique et une publication explicite par base MOSIP ; tables et colonnes listées
  une à une (minimisation) ; secrets hors dépôt.
- Job PySpark : schémas explicites, checkpoint durable, lot et registre écrits dans la même transaction, faits
  recalculés depuis l'état courant : un rejeu ou un redémarrage ne compte rien deux fois.
- Surveillance : WAL retenu par le slot, retard Debezium, retard Kafka, progression Spark, rejets, fraîcheur
  (`bi.source_fraicheur`).
- Détail, modèles de configuration et procédures d'exploitation : skill `mosip-bi-pipeline`.

## API
- REST JSON sous `/api/v1`, une ressource par page et par bloc (ex. `/api/v1/enrolement/devenir?du=…&au=…&zone=…`).
- Paramètres communs : `du`, `au` (dates ISO, bornés aux données), `zone` (code), filtres propres à la page.
- Réponses : valeurs brutes (nombres), jamais de texte formaté ; le front formate.
- Erreurs au format Problem Details (RFC 9457).
- Sécurité : resource server OAuth2 ; rôles `bi-national` / `bi-regional` ; un utilisateur régional ne peut pas demander
  une autre zone (contrôle côté API, test obligatoire).
- Documentation : `/swagger-ui.html`, contrat `/v3/api-docs`.

## Front
- Routes : `/` (Vue d'ensemble), `/enrolement`, `/impression-cartes`, `/abis`, `/idps`, `/authentifications`, `/exploration`.
- Les filtres (période, zone…) vivent dans l'adresse : une vue filtrée se partage par lien.
- Données via TanStack Query (clé = ressource + filtres) ; types générés depuis l'OpenAPI.
- Composants partagés : coque (en-tête, bandeau, pied), filtre Période, carte KPI, tableau, carte du Togo, graphiques ECharts.

## Environnements
- Développement : `deploy/docker-compose.yml` (PostgreSQL BI ; Keycloak de test avec le profil `auth`), back et front lancés localement.
  Kafka, Kafka Connect et Spark n'y figurent pas encore.
- Recette et production : images Docker, Helm, cluster Kubernetes de MOSIP, Keycloak existant (realm de l'ANID).
  Plateforme Kafka, Kafka Connect et Spark : à préciser avec l'exploitation.
