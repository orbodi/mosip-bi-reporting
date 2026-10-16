# Décisions

Chaque décision : date, choix, raison. Ajouter les nouvelles en bas de la section concernée.

## Architecture et technologies
- 2026-10-13 : **Back en Java 21 et Spring Boot 4** (Maven). Même technologie que MOSIP : l'équipe d'exploitation la connaît.
- 2026-10-13 : **Front en React 19, TypeScript et Vite** : application monopage derrière Keycloak, sans rendu serveur.
- 2026-10-13 : **Base BI PostgreSQL dédiée**, schéma `bi`. L'API et le front ne lisent jamais les bases MOSIP de production.
  3,3 millions d'inscriptions : PostgreSQL suffit. ClickHouse seulement si l'Exploration devient lente.
- 2026-10-13 : **Alimentation** : extraction des tables MOSIP utiles (réplication ou extraction nocturne), transformations en SQL
  versionné avec **dbt** et tests de réconciliation ; scripts dédiés pour les journaux ABIS (IN Groupe) et IDPS.
  **Remplacée le 16/10/2026 pour les bases MOSIP** (décision suivante).
- 2026-10-16 : **Alimentation des bases MOSIP par capture des changements (CDC)** : EDB PostgreSQL → Debezium
  (connecteur PostgreSQL, `pgoutput`, un slot logique et une publication explicite par base) → Kafka → PySpark
  Structured Streaming → Data Mart PostgreSQL (schémas `etat`, `pipeline`, `bi`) → API. Architecture cible demandée
  le 15/10/2026. Principes : état courant idempotent (garde sur le LSN), registre des lots écrit dans la même
  transaction, faits recalculés depuis l'état courant et jamais incrémentés par événement (pas de double comptage au
  rejeu ni au redémarrage). Tests : pytest sur un vrai PostgreSQL (rejeu, redémarrage, suppressions) et contrôles de
  qualité en production ; ils remplaceront les tests dbt. Journaux ABIS et IDPS : scripts dédiés, inchangé. L'ébauche
  dbt de `pipeline/` reste jusqu'au remplacement ; son retrait se décide ici. Guide : skill `mosip-bi-pipeline`.
- 2026-10-16 : **Pseudonymisation dans le pipeline** : Debezium ne masque pas la clé des messages, donc le RID passe en
  clair dans Kafka. Accès aux topics réservé au pipeline (ACL) ; le job Spark dérive centre et machine du RID puis le
  remplace par une empreinte HMAC-SHA-256 (clé secrète hors dépôt). Le RID complet n'est jamais écrit dans le Data Mart.
- 2026-10-16 : **Premier flux temps réel : enrôlement, en local** (Docker Desktop, profil `temps-reel` de
  `deploy/docker-compose.yml`) : base MOSIP simulée au DDL officiel de `regprc.registration`, Debezium 3.7, Kafka 4.1,
  job PySpark (lot toutes les 10 s), migration `V2`, API `/api/v1/enrolement/devenir`, bloc « Devenir des
  inscriptions » relu toutes les 30 s. Règles provisoires : jour = `cr_dtimes` ; correspondance des statuts
  PROCESSED → abouti, PROCESSING → en cours, REJECTED → rejeté, FAILED et REPROCESS_FAILED → échoué, chargée **en
  développement seulement** (vide ailleurs tant que l'équipe MOSIP ne l'a pas validée).
- 2026-10-13 : **Authentification Keycloak** (OIDC, PKCE côté front, jetons vérifiés par l'API). Rôles prévus :
  `bi-national` (tout le Togo) et `bi-regional` avec un attribut `zone` (code de région). Le filtre de zone est appliqué par l'API.
- 2026-10-13 : **Contrat d'API** : OpenAPI généré par springdoc ; types TypeScript générés avec openapi-typescript.
- 2026-10-13 : **Bibliothèques front** : TanStack Query (cache des données), TanStack Router (filtres dans l'adresse),
  React Aria Components (listes, onglets, dates accessibles au clavier), Apache ECharts (graphiques et carte),
  TanStack Table (tableaux et tableau croisé de l'Exploration, à ajouter avec la première page qui en a besoin).
- 2026-10-13 : **Tests** : JUnit et Testcontainers (back) ; Vitest et Testing Library (front) ; Playwright et axe (parcours,
  captures aux trois largeurs, accessibilité) ; tests dbt (réconciliation des chiffres), remplacés par les tests du
  pipeline CDC (décision du 16/10/2026).
- 2026-10-13 : Déploiement visé : images Docker et Helm sur le cluster Kubernetes de MOSIP, Keycloak existant.

## Charte
- Bleu ANID adouci `#1F4E8C` (remplace `#013781` depuis le 9 oct. 2026), bleu nuit `#071B35` pour le texte,
  jaune ANID `#FCBA21`, fond `#F1F4F6`, police Poppins. Détail dans `docs/charte.md`.

## Règles d'affichage retenues pendant la maquette
- Nombre d'abord, pourcentage en complément ; pas de pourcentage sous une base 100 % (ex. « Inscriptions » dans la frise).
- Filtre Période sur chaque page : Depuis le début, 7, 30 et 90 derniers jours (jusqu'à la dernière mise à jour de la page),
  Période personnalisée (dates « Du » et « au », bornées aux données disponibles).
- Les blocs qui ne suivent pas un filtre l'indiquent par une pastille (« Ensemble du Togo », « Au 14/01/2026, hors filtre Période »).
- Pastille « Dernière mise à jour : date à heure » par page, avec l'heure de la dernière donnée de la source principale.
- Libellés IN Groupe conservés sur la page ABIS (HIT, NO HIT, Face, Fingerprint…).

## Anomalies connues (à afficher et signaler, jamais à corriger dans le BI)
- Demandes d'impression 3 113 431 supérieures aux NIU 3 058 886 (écart 54 545) : à réconcilier (réimpressions ? doublons ?).
- Top des centres : plus de cartes expédiées que d'inscriptions dans 4 des 5 centres (ex. Doumassesse 44 370 contre 43 534).
- Rejet d'impression daté du 13/03/2026, après l'arrêt des autres données (14/01/2026) : à vérifier.
- Dernier événement différent selon la source : enrôlement 14/01/2026, scores biométriques 29/06, IDPS 03/07, ABIS 13/07/2026.
- « Synchronisés mais non chargés » négatif (−16 734) dans le BI actuel : à compter par jointure.
- Statuts en doublon dans le BI actuel (Traité/Réussi…) : probable mélange `status_code` / `latest_trn_status_code`.
- Taux d'échec des authentifications de 57,7 %.
- IDPS : 14 ordres, tous en erreur et en attente, tous en Savanes le 03/07/2026 (circuit pilote).

## À trancher avant ou pendant le développement (revue UI/UX du 9 oct. 2026)
1. Dictionnaire des indicateurs complet (définition, dénominateur, libellé, fraîcheur par source) — amorcé dans `docs/indicateurs.md`.
2. Portée des filtres et affichage de l'état filtré.
3. Échelle typographique (7 tailles + 2 tailles de KPI) — proposée dans `docs/charte.md`.
4. Jetons de couleur (neutres, marque, sémantiques, data-viz, couleur fixe par indicateur) — proposés dans `jetons.css`.
5. Un seul composant Tableau (total, région cliquable, ordre, mobile).
6. Patron KPI (nombre avant %, composant Alerte avec seuil).
7. Interactions (onglets, listes, carte) et modèle clavier.
8. Responsive (2 colonnes jusqu'à 900 px, menu et filtres mobiles).

## À trancher pour le pipeline CDC (16 oct. 2026)
1. **Sexe et âge** : `anonymous_profile` n'existe pas en MOSIP 1.1.5 (`idrepo.anonymous_profile` à partir de 1.1.5.5,
   `regprc.anonymous_profile` en 1.2.0). Options : vérifier la version exacte de l'instance, mise à niveau, ou flux
   anonymisé fourni par l'équipe MOSIP. Proposition en attendant : les filtres Genre et Âge et la pyramide des âges de
   la maquette affichent « non disponible ». `regprc.individual_demographic_dedup` (seule colonne de sexe en 1.1.5)
   reste exclue : elle contient des données d'identité.
2. **Sources des pré-inscriptions et des NIU** : `prereg.applicant_demographic` et `idrepo.uin` portent des données
   d'identité ; le skill `mosip-bi-pipeline` les exclut de la capture. Trouver une autre source (ex. `reg_appointment`,
   `registration` aboutie) ou accorder une dérogation limitée à quelques colonnes (identifiant, statut, dates),
   validée par la sécurité.
3. **Dérogation d'écriture dans la base MOSIP** pour les tables techniques `bi_cdc.heartbeat` et
   `bi_cdc.debezium_signal` (avancement du slot quand les tables capturées sont calmes ; snapshots incrémentaux).
   Sans dérogation : `snapshot.mode=initial`, heartbeat sans requête, surveillance du WAL retenu, et toute reprise
   passe par un nouveau slot et un snapshot complet.
4. **« Par statut, chaque jour »** : cohorte (où en sont aujourd'hui les inscriptions du jour J ; les chiffres passés
   évoluent) ou photo (statuts à la fin du jour J, instantané figé chaque soir, sans reconstitution du passé).
5. **Regroupement des statuts** : relever les `status_code` et `latest_trn_status_code` présents sur l'instance, puis
   faire valider la correspondance vers abouti, rejeté, échoué, en cours par l'équipe MOSIP
   (table `pipeline.correspondance_statut`).
6. **Date de rattachement d'une inscription** : `pkt_cr_dtimes` (création du paquet au centre) ou `cr_dtimes`
   (réception par MOSIP), et fuseau des horodatages.
7. **Retrait de l'ébauche dbt** quand le flux CDC de l'enrôlement tourne en recette ; mettre à jour en même temps le
   skill `nouveau-kpi`, l'agent `auditeur-donnees` et la permission `Bash(dbt *)` de `.claude/settings.json`, qui
   citent encore dbt.
