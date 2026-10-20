# BI Reporting ANID (MOSIP, Togo)

Tableau de bord décisionnel de l'Agence nationale d'identification (ANID) du Togo, alimenté par MOSIP
(enrôlement, NIU, impression des cartes, ABIS, IDPS, authentifications). Il remplace le BI existant
et reprend la maquette validée en octobre 2026 (dossier `maquette/`).

## Structure
- `backend/` : API Spring Boot 4, Java 21, Maven. Lit uniquement la base BI (schéma `bi`). Voir `backend/CLAUDE.md`.
- `frontend/` : React 19, TypeScript, Vite. Voir `frontend/CLAUDE.md`.
- `pipeline/` : alimentation du Data Mart. Bases MOSIP : capture des changements (Debezium → Kafka → PySpark Structured
  Streaming), voir le skill `/mosip-bi-pipeline`. Journaux ABIS et IDPS : scripts dédiés. L'ébauche par lots (dbt,
  `publier.sql`) date d'avant ce choix : ne pas l'étendre (voir `docs/decisions.md`).
- `deploy/` : Docker Compose de développement (PostgreSQL BI, Keycloak de test, chaîne temps réel avec MOSIP simulée).
- `maquette/` : référence visuelle (pages, captures, fichier de présentation). Ne pas modifier.
- `docs/` : décisions, architecture, structure du Data Mart, dictionnaire des indicateurs, sources MOSIP, charte.

## Commandes
- Base BI locale : `docker compose -f deploy/docker-compose.yml up -d postgres`
- Backend : `cd backend && mvn spring-boot:run -Dspring-boot.run.profiles=dev` (port 8080)
- Tests backend : `mvn test` (unitaires), `mvn verify` (avec tests d'intégration Testcontainers, Docker requis)
- Frontend : `cd frontend && npm run dev` (port 5173, `/api` redirigé vers 8080)
- Vérifications frontend : `npm run lint`, `npm run typecheck`, `npm test`, `npm run test:e2e`
- Chaîne temps réel locale (MOSIP simulée → Debezium → Kafka → Spark → API → page) :
  `docker compose -f deploy/docker-compose.yml --profile temps-reel up -d --build`, vérification
  `docker compose -f deploy/docker-compose.yml run --rm outils` (voir `pipeline/README.md`)
- Tests du pipeline : `cd pipeline && python -m pytest` (PostgreSQL local requis)
- Types de l'API : `npm run api:types` (backend démarré) régénère `frontend/src/api/schema.ts`

## Règles métier (à respecter partout)
- Le dictionnaire `docs/indicateurs.md` fait foi : définition, source, calcul et dénominateur de chaque indicateur.
  Un nouvel indicateur commence par sa fiche dans ce fichier (skill `/nouveau-kpi`).
- Les chiffres doivent concorder entre les pages et avec l'Exploration. Ils viennent tous des mêmes tables agrégées.
- Ne jamais « corriger » une anomalie de données : l'afficher telle quelle et la signaler (note ou pastille),
  puis la consigner dans `docs/decisions.md` (section Anomalies).
- Données personnelles : aucune donnée nominative ni biométrique dans la base BI ni dans l'interface.
  RID et identifiants d'agents pseudonymisés (empreinte HMAC calculée dans le pipeline). Le RID passe en clair dans la
  clé des messages Kafka (Debezium ne masque pas les clés) : accès aux topics réservé au pipeline.
- Sexe et âge : seule source, le profil anonymisé de MOSIP `idrepo.anonymous_profile` (1.1.5.5 et plus ; décision du
  20/10/2026), réduit à processus, jour, genre, tranche d'âge et région. Sans lui, « inconnu » dans le Data Mart.
  Ne jamais lire pour cela `individual_demographic_dedup`, `uin_data`, `demog_detail` ni les paquets.
- Valeur indisponible : `null` dans l'API, affichée 0 dans le BI, sans note (décision du 20/10/2026).
- Jamais d'écriture dans les bases MOSIP. Le BI les lit par réplication logique : rôle dédié sans superutilisateur,
  `SELECT` sur les seules tables capturées, publication créée par le DBA. Une écriture (tables de heartbeat ou de
  signal Debezium) demande une dérogation écrite dans `docs/decisions.md`. L'API et le front ne lisent que la base BI.
- Production MOSIP : Claude prépare les scripts et les demandes (slot, publication, paramètres, snapshot) ; le DBA ou
  l'exploitation les exécute après validation de chaque action. Aucune migration destructive sans validation explicite.
- La portée géographique de l'utilisateur (rôle Keycloak) est appliquée par l'API, jamais seulement par le front.

## Règles d'affichage
- Interface en français. Nombres au format fr-FR avec espace fine insécable (`3 278 239`), une décimale pour les
  pourcentages (`54,0 %`), dates `14/01/2026`, heures `11h59`. Utiliser `frontend/src/lib/format.ts`.
- Le nombre d'abord, le pourcentage en complément.
- Libellés exacts de la maquette (ex. « Cartes remises », « Impression des cartes », « NIU générés »).
- Couleurs et typographie : uniquement les jetons de `frontend/src/styles/jetons.css` (voir `docs/charte.md`).
- Accessibilité WCAG 2.1 AA : contraste 4,5:1 pour le texte, tout au clavier, cibles de 44 px sur mobile.
- Trois largeurs de référence : 1 440, 1 000 et 390 px.

## Façon de travailler
- Pour une page ou un module : mode plan d'abord, en s'appuyant sur la page de la maquette et sur le dictionnaire.
- Équipe d'agents (`.claude/agents/`) : `tech-lead` cadre le lot (plan dans `docs/plans/`, décisions à poser),
  puis `data-engineer` → `dev-backend` → `dev-front` → `qa-testeur` ; revues `auditeur-donnees`, `expert-uiux`,
  `relecteur-securite`. Les questions métier se tranchent avec l'humain, jamais par un agent.
- Une tâche par session ; `/clear` entre deux sujets sans rapport.
- Avant de rendre la main : tests et vérification des types au vert (le hook Stop les lance).
- Comparer le rendu à la maquette avec `/verif-visuelle` dès qu'une page change.
- Écrire les messages de commit en français, à l'impératif (« Ajoute l'API des inscriptions par région »).

## Références
- Décisions et anomalies connues : @docs/decisions.md
- Dictionnaire des indicateurs : @docs/indicateurs.md
- Structure du Data Mart (tables par domaine, grains, colonnes MOSIP retenues, décisions ouvertes) : docs/datamart.md
- Architecture : docs/architecture.md ; sources MOSIP et journaux ABIS : docs/sources-mosip.md ; pipeline CDC :
  skill `/mosip-bi-pipeline`
- Charte : docs/charte.md ; revue UI/UX : docs/revue-uiux.md ; historique de la maquette : docs/historique-maquette.md
