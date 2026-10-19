# BI Reporting ANID : tableau de bord seul (données fictives)

Branche `dashboard` : l'interface (`frontend/`) et l'API (`backend/`) du BI, sans le pipeline MOSIP. La base est
remplie au démarrage avec des **données fictives** : environ 3,3 millions d'inscriptions sur deux ans
(01/01/2024 → 14/01/2026), réparties sur des centres de démonstration. Aucune donnée réelle, aucune donnée personnelle.

Le développement continue sur `main` ; cette branche sert à montrer et tester le tableau de bord.

## Démarrer avec Docker

Prérequis : Docker. Ports utilisés sur la machine : 5432, 8080 et 5173. S'ils sont déjà pris (autre service,
environnement de `main`), choisir d'autres ports : `API_PORT=8081 FRONT_PORT=5174 PG_PORT=5433 docker compose up -d`.
Pour ouvrir l'interface depuis un autre poste par le nom du serveur, ajouter `FRONT_HOTE=<nom du serveur>` ;
par l'adresse IP, rien à faire.

```
docker compose up -d
docker compose logs -f api      # attendre « Started BiApplication »
```

Puis ouvrir http://localhost:5173/enrolement. Le premier démarrage prend quelques minutes (téléchargement des
dépendances Maven et npm, puis génération des données fictives, une quinzaine de secondes) ; les suivants sont rapides.

- Arrêter : `docker compose down` (les données restent).
- Repartir d'une base vide : `docker compose down -v`, puis `docker compose up -d`.
- Documentation de l'API : http://localhost:8080/swagger-ui.html

## Démarrer sans Docker

Prérequis : Java 21, Maven, Node 22, et un PostgreSQL local avec une base `bi` (utilisateur `bi`, mot de passe `bi`).

```
cd backend && mvn spring-boot:run -Dspring-boot.run.profiles=dev,demo      # API sur 8080
cd frontend && npm ci && npm run dev                                        # interface sur 5173
```

## Ce que l'on voit

- **Enrôlement** : devenir des inscriptions, inscriptions et NIU par semaine, territoire (carte et tableau par région
  puis par préfecture), âge et sexe (« non disponible », règle du projet), top des centres, filtres Période et Région.
  Le bloc Pré-inscription reste à construire (source à décider).
- Les autres onglets affichent la liste des blocs prévus, d'après la maquette.

Sécurité Keycloak désactivée (profil `dev`) : tout le monde voit le niveau national. Ne jamais déployer cette
configuration en recette ni en production.
