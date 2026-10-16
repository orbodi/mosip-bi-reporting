# MOSIP BI Reporting

Tableau de bord décisionnel de l'Agence nationale d'identification du Togo, alimenté par MOSIP.
Java 21 / Spring Boot 4 (API), React 19 / TypeScript (interface), PostgreSQL (base BI), Debezium, Kafka et PySpark (pipeline), Keycloak.

## Démarrer en local
Prérequis : Java 21, Maven 3.9+, Node 22+, Docker.

```bash
docker compose -f deploy/docker-compose.yml up -d postgres          # base BI (bi / bi)
cd backend  && mvn spring-boot:run -Dspring-boot.run.profiles=dev   # API sur :8080, migrations + données de démo
cd frontend && npm ci && npm run dev                                # interface sur :5173
```

Ouvrir http://localhost:5173. Le profil dev désactive la connexion ; pour la tester, voir `deploy/keycloak/README.md`.

Chaîne temps réel complète en conteneurs (MOSIP simulée, Debezium, Kafka, Spark, API, interface), sans Java ni Node
sur le poste : `docker compose -f deploy/docker-compose.yml --profile temps-reel up -d --build`, puis
http://localhost:5173/enrolement. Détails et vérification : `pipeline/README.md`.

## Arborescence
| Dossier | Rôle |
|---|---|
| `backend/` | API REST en lecture seule sur la base BI (`/api/v1/...`, Swagger sur `/swagger-ui.html`) |
| `frontend/` | Application React : coque ANID, 7 pages, filtre Période, connexion Keycloak |
| `pipeline/` | Capture des changements MOSIP (Debezium, Kafka, PySpark) vers le Data Mart, scripts des journaux ABIS et IDPS ; ébauche dbt antérieure, à remplacer |
| `deploy/` | Docker Compose de développement, realm Keycloak de test |
| `maquette/` | Maquette validée : fichier de présentation, captures, sources des pages |
| `docs/` | Décisions, architecture, dictionnaire des indicateurs, sources MOSIP, charte, feuille de route |
| `.claude/` | Configuration Claude Code : permissions, hooks, skills, agents |

## Tests
- Backend : `mvn test` (unitaires), `mvn verify` (intégration, Docker requis).
- Frontend : `npm run lint`, `npm run typecheck`, `npm test`, `npm run test:e2e` (parcours, accessibilité, 3 largeurs).
- Pipeline : `cd pipeline && python -m pytest` (job temps réel et simulateur, PostgreSQL requis) ; `dbt build` pour
  l'ébauche par lots antérieure.
La CI (`.github/workflows/ci.yml`) lance tout à chaque pull request.

## Travailler avec Claude Code
Lancer `claude` à la racine du dépôt. Il lit `CLAUDE.md` (règles du projet) puis `backend/CLAUDE.md` ou
`frontend/CLAUDE.md` selon les fichiers touchés.

- **Skills** : `/nouveau-kpi <indicateur>` (de la fiche du dictionnaire à la page), `/verif-visuelle <page>`
  (comparaison à la maquette), `/demarrer` (environnement local), `/mosip-bi-pipeline` (pipeline CDC : Debezium,
  Kafka, PySpark, Data Mart, exploitation).
- **Agents** : `expert-uiux` (revue d'une page), `auditeur-donnees` (concordance des chiffres),
  `relecteur-securite` (Keycloak, portée régionale, données personnelles). Exemple : « demande à l'agent
  auditeur-donnees de vérifier l'API des inscriptions ».
- **Hooks** : formatage et lint après chaque modification du front ; tests au moment de rendre la main ;
  blocage des fichiers `.env`, de la maquette et des migrations déjà versionnées.
- **Serveurs MCP** (`.mcp.json`, à approuver au premier lancement) : `base-bi` (lecture seule sur la base locale,
  rôle `bi_lecture`) et `playwright` (navigateur pour vérifier les pages).
- Méthode conseillée : mode plan (Maj+Tab) avant chaque page, une session par tâche, `/clear` entre deux sujets,
  worktrees (`claude -w <nom>`) pour avancer plusieurs pages en parallèle. Relecture des pull requests par Claude :
  `/install-github-app`.

## Première mise en route
1. Créer le dépôt Git, committer ce socle.
2. `mvn -N wrapper:wrapper` dans `backend/` pour ajouter le wrapper Maven (`./mvnw`), puis `mvn verify`.
3. Suivre `docs/feuille-de-route.md`.
