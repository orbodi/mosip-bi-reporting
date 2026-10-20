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
- 2026-10-19 : **Page Enrôlement, données de démonstration** (plan `docs/plans/enrolement.md`). « NIU par semaine »
  en lecture flux : NIU rattachés à leur jour de génération, table `bi.fait_niu_jour` (migration `V3`), vide hors
  démonstration tant que le lot A ne l'alimente pas (l'API le signale par `niuDisponibles`, le front n'affiche alors
  pas de courbe). Filtre Région porté par l'adresse (`?region=`), liste servie par `GET /api/v1/meta/regions` selon la
  portée Keycloak ; Territoire, Âge et sexe et Top des centres le suivent ; Pré-inscription, Devenir et Semaines
  restent nationaux avec la pastille « Ensemble du Togo » (comme la maquette).
- 2026-10-19 : **Profil `demo` séparé du profil `dev`** (`application-demo.yml`, `db/demo/R__volumes_demo.sql`) : deux
  ans d'inscriptions fictives générées en SQL pour la page Enrôlement. Séparé parce que ces faits ne viennent pas de
  `etat.registration` : le contrôle « état courant = faits » de la chaîne temps réel échouerait. Le script refuse de
  tourner sur une base déjà alimentée par le pipeline. Lancement : `mvn spring-boot:run -Dspring-boot.run.profiles=dev,demo`.
- 2026-10-19 : **Carte du Togo avec ECharts** sur un fond SVG nommé (contours de la maquette, © contributeurs
  OpenStreetMap, geoBoundaries ; 37 préfectures), ECharts chargé à la demande (paquet séparé). Les zones de l'API sont
  reliées aux contours par leur nom en attendant les codes de `master.location` ; une zone sans contour est citée sous
  la carte. Préfectures et centres de développement : codes provisoires (`SAV-01`…) dans `R__donnees_dev.sql`.
- 2026-10-20 : **Pré-inscriptions : dérogation limitée sur `prereg.applicant_demographic` et `_consumed`** (décision
  du responsable du projet ; points 1 et 2 du pipeline CDC ci-dessous). Seules les colonnes `prereg_id` (empreinte
  HMAC dans Spark), `status_code`, `cr_dtimes` et `upd_dtimes` sont capturées : `column.include.list` du connecteur
  `prereg-dev.json`, publication et `SELECT` limités aux mêmes colonnes (`pipeline/cdc/connecteurs/prerequis-prereg.sql`).
  `demog_detail` (chiffrée), `demog_detail_hash` et `cr_appuser_id` ne sont jamais lues. Raison donnée : les données
  d'identité sont chiffrées et ne sont pas traitées. Statuts regroupés par `pipeline.correspondance_statut_preinscription`
  (à valider par l'équipe MOSIP ; « non classées » sinon) ; « Honorées à l'inscription » = demandes passées dans
  `_consumed`. Migration `V4`, job `streaming/preinscription`, API `GET /api/v1/enrolement/preinscriptions`. À faire
  avant la recette : revue par le relecteur sécurité, exécution des prérequis par le DBA. Le sexe des pré-inscriptions
  reste sans source (il n'est que dans `demog_detail`) : « Femmes pré-inscrites » non disponible.
- 2026-10-20 : **Sexe et âge des NIU : profil anonymisé de MOSIP** (`idrepo.anonymous_profile`, MOSIP 1.1.5.5 et plus ;
  point 1 du pipeline CDC). Option recommandée retenue, sans préférence exprimée. Un profil « New » = un NIU généré,
  au jour du champ `date` du profil ; âge = année de ce jour − `yearOfBirth` ; région résolue depuis `bi.zone` à
  partir de `location`. Minimisation : le JSON, l'année de naissance et les codes de lieux ne sont jamais écrits
  (`etat.profil_anonyme` ne garde que processus, jour, genre, tranche et région). Genre regroupé par
  `pipeline.correspondance_sexe` (à valider ; « I » sinon). Migration `V4`, job `streaming/profil`, API
  `GET /api/v1/enrolement/age-sexe` (Togo ou une région). Préalable : vérifier que l'instance a la table (partie A de
  `prerequis-idrepo.sql`) ; sinon mise à niveau en 1.1.5.5, ou agrégat quotidien livré par l'équipe MOSIP chargé dans
  la même table `bi.fait_niu_profil_jour`. Le profil contient d'autres champs (biométrie, documents) qui transitent
  par Kafka : topic à accès restreint comme les autres ; vérifier avec la sécurité le correctif MOSIP de l'anomalie
  « Anonymous Profile - Possible Data Leakage » (id-repository, ticket 1685) sur la version déployée.
- 2026-10-20 : **Tranches d'âge : les 8 de la maquette** (0-5, 6-14, 15-18, 19-25, 26-35, 36-45, 46-60, 60 et +), au
  lieu des 5 du dictionnaire. Les libellés de la maquette se chevauchent à 60 ans : 60 ans compte dans « 46 à 60 »,
  « 60 ans et + » à partir de 61 ans. Recommandation retenue, sans préférence exprimée.
- 2026-10-20 : **Valeurs indisponibles affichées 0 dans le BI, sans note** (demande du responsable du projet) : plus de
  « – » ni de notes « source pas encore raccordée », « non disponible » ou « chiffres indisponibles ». Les barres, la
  carte et la pyramide restent vides (aucune forme estimée) ; noms et dates inconnus gardent « – ». L'API garde la
  différence : `null` (indisponible) n'est jamais 0. Revient sur la note « non disponible » de la règle Sexe et âge
  (CLAUDE.md mis à jour). Risque accepté : un 0 affiché ne se distingue plus d'un vrai zéro.
- 2026-10-20 : **Front des sept pages (branche `dashboard`)** : l'Exploration garde ses choix (source, indicateurs,
  ventilation) dans l'état de la page et non dans l'adresse, par exception à la règle du front ; jetons ajoutés
  `--serie-3` (vert des hommes et des courbes) et `--rouge-fonce` ; le chiffre clé de la Vue d'ensemble passe en
  `--encre-2` (contraste 4,5:1 sur le fond doré).

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
- Pré-inscription (relevés du 14/10/2026 sur `mosip_prereg`, comptages seuls) : `appointment_date` vaut 31/12/9999
  pour tous les rendez-vous, actifs et consommés (« Expirées » restera à 0, seul `booking_dtimes` est exploitable) ;
  444 pré-inscriptions ont plusieurs lignes de rendez-vous, toujours pour le même centre (double envoi en mai 2025,
  re-réservation encore active en septembre 2026 : compter en `count(distinct prereg_id)`) ; 2 245 rendez-vous sans
  pré-inscription ; 1 144 pré-inscriptions « Pending_Appointment » avec rendez-vous et 268 « Booked » sans rendez-vous ;
  aucun statut `Expired` ni `Cancelled`.
- Base `mosip_prereg` : tables de copie hors DDL officiel (`applicant_demographic_consumed_16102025`, `asi_app`,
  `asi_doc`) à exclure de toute capture ; `processed_prereg_list` du DDL officiel absente de l'instance ; une
  publication `dbz_publication` existe déjà et couvre des tables exclues de la capture (à revoir avec le DBA).

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
1. **Sexe et âge** (tranché le 20/10/2026 : profil anonymisé, voir plus haut) : `anonymous_profile` n'existe pas en
   MOSIP 1.1.5 (`idrepo.anonymous_profile` à partir de 1.1.5.5, `regprc.anonymous_profile` en 1.2.0). Options : vérifier la version exacte de l'instance, mise à niveau, ou flux
   anonymisé fourni par l'équipe MOSIP. Proposition en attendant : les filtres Genre et Âge et la pyramide des âges de
   la maquette affichent « non disponible ». `regprc.individual_demographic_dedup` (seule colonne de sexe en 1.1.5)
   reste exclue : elle contient des données d'identité.
2. **Sources des pré-inscriptions et des NIU** (pré-inscriptions tranchées le 20/10/2026 : dérogation limitée, voir
   plus haut ; NIU : toujours ouvert) : `prereg.applicant_demographic` et `idrepo.uin` portent des données
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
7. **Retrait de l'ébauche dbt** quand le flux CDC de l'enrôlement tourne en recette ; retirer en même temps
   la permission `Bash(dbt *)` de `.claude/settings.json`. Le skill `nouveau-kpi` et l'agent `auditeur-donnees` ne
   citent plus dbt depuis le 16/10/2026 (structure du Data Mart : `docs/datamart.md`).
