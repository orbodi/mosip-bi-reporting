# Feuille de route

Chaque étape se termine par des tests au vert et une comparaison à la maquette.

1. **Socle** (ce dépôt) : coque de l'application, connexion Keycloak, base BI et migrations, CI. Livré le 14 oct. 2026.
   Vérifié à la livraison : front (lint, types, 12 tests Vitest, 9 parcours Playwright avec axe aux trois largeurs) ;
   migration, données de démo et rôle en lecture seule sur PostgreSQL ; `dbt build` et `publier.sql` sur des données
   factices ; hooks Claude Code. **Non vérifié** : la compilation Java (Maven Central inaccessible depuis
   l'environnement de génération). Première action : `mvn verify` dans `backend/` et corriger si besoin
   (points sensibles : compatibilité springdoc 3.0.1 avec Spring Boot 4.1.0, noms des starters de Boot 4).
2. **Données réelles** (16/10/2026 : premier flux temps réel de l'enrôlement en local, sur MOSIP simulée) :
   inventaire du catalogue MOSIP en recette (script du skill `mosip-bi-pipeline`, passé par un DBA) ; trancher les
   points « pipeline CDC » de `docs/decisions.md` ; premier flux CDC en recette (connecteur Debezium sur
   `regprc.registration`, job PySpark, schémas `etat` et `pipeline`) avec ses tests ; retrouver les valeurs de
   référence de `docs/indicateurs.md`.
3. **Composants partagés** : filtre Période (dates « Du » / « au »), carte KPI, tableau unique, carte du Togo,
   graphique hebdomadaire ; captures comparées à la maquette aux trois largeurs.
4. **Page modèle : Enrôlement de bout en bout** (flux CDC → table `bi.fait_enrolement_jour` → API → page). Elle sert de patron.
5. **Vue d'ensemble** (frise du parcours, cartes des modules, parcours par région).
6. **Autres pages en parallèle** (une session ou un worktree par page) : Impression des cartes, Authentifications, IDPS, ABIS.
7. **Exploration** (onglets par source, filtres en cascade, tableau croisé, export CSV).
8. **Recette** : revue UI/UX et accessibilité (agent `expert-uiux`), revue de sécurité (agent `relecteur-securite`),
   charge sur l'Exploration, déploiement Helm ; exploitation du pipeline (runbook, alertes sur le WAL retenu et le
   retard) et prérequis de production validés action par action avec le DBA.
