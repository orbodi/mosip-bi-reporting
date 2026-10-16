---
name: demarrer
description: Démarre l'environnement de développement local (base BI PostgreSQL, API Spring Boot en profil dev, front Vite) et vérifie que tout répond.
disable-model-invocation: true
---

# Démarrer l'environnement local

1. Base BI : `docker compose -f deploy/docker-compose.yml up -d postgres`, puis attendre que
   `docker compose -f deploy/docker-compose.yml ps` indique `healthy`.
2. API (en arrière-plan) : `cd backend && mvn spring-boot:run -Dspring-boot.run.profiles=dev`.
   Attendre que `curl -s localhost:8080/actuator/health` renvoie `{"status":"UP"}` ;
   `curl -s localhost:8080/api/v1/meta` doit lister 5 sources.
3. Front (en arrière-plan) : `cd frontend && npm ci` si `node_modules` manque, puis `npm run dev`.
   L'application est sur http://localhost:5173.
4. Connexion Keycloak (facultatif) : `docker compose -f deploy/docker-compose.yml --profile auth up -d keycloak`,
   puis relancer l'API avec `BI_SECURITE_ACTIVE=true` et le front avec `VITE_AUTH_ACTIVE=true`.
   Compte de test : voir `deploy/keycloak/README.md`.
5. Résumer à l'humain ce qui tourne (adresses) et ce qui a échoué, avec la cause.
