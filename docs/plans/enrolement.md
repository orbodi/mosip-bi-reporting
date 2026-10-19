# Plan : terminer la page Enrôlement (données de démonstration)

Date : 19/10/2026. Statut : **en cours**. P2 et P3 retenus le 19/10/2026 (sans préférence de l'humain : propositions ci-dessous) ;
P1 en attente.

## Objet

Construire les cinq blocs restants de la page Enrôlement, dans l'ordre de la maquette, avec des données de
démonstration chargées par le profil `dev` (aucune donnée réelle), et ajouter le filtre Région au bandeau.
Le bloc « Devenir des inscriptions » existe déjà et ne change pas.

Références : `maquette/pages/Enrolement.dc.html` et `maquette/captures/Enrolement-*.png`, `docs/indicateurs.md`
(section Enrôlement), `docs/datamart.md` (§ 5.1, 5.2, 7, 8, 9), `docs/decisions.md`. Un prototype cliquable des
7 pages (hors dépôt, React 18, données générées dans le navigateur) sert de référence de mise en page ; son code
n'est pas repris tel quel (pile et conventions différentes).

## Décisions à prendre par l'humain avant de coder

| N° | Question | Proposition |
|---|---|---|
| P1 | Pré-inscription : capturer `applicant_demographic` et `_consumed` sur les seules colonnes sans identité (`prereg_id` en empreinte, `status_code`, `cr_dtimes`, `upd_dtimes`, `lang_code`) ? (décision 1 de `docs/datamart.md`) | Construire le bloc sur ce contrat avec les données de démonstration. Tant que la dérogation n'est pas validée par la sécurité, l'API renvoie `null` hors `dev` pour les demandes et statuts, et le bloc affiche « non disponible » ; les rendez-vous (`reg_appointment`, déjà autorisée) restent affichés. |
| P2 | « Inscriptions et NIU par semaine » : lecture cohorte (NIU rattachés au jour de réception, table existante) ou flux (jour de génération du NIU, nouvelle table `bi.fait_niu_jour`) ? | Flux, comme la maquette (la courbe NIU décroche sur les semaines récentes) : créer `bi.fait_niu_jour` dès ce lot. |
| P3 | Portée du filtre Région (point 2 de la revue UI/UX) : quels blocs le suivent ? | Comme la maquette : Territoire, Âge et sexe, Top des centres le suivent ; Pré-inscription (pas de centre), Devenir et semaines restent nationaux avec la pastille « Ensemble du Togo ». |

Déjà tranché par les règles du projet : sexe et âge « non disponible » (décision 11) ; codes de région de `bi.zone`
(`GLO` pour Grand Lomé) ; aucune anomalie corrigée, seulement affichée et consignée.

## Anomalies relevées sur la base de pré-inscription (à consigner dans `docs/decisions.md`)

Constats du 14/10/2026 sur `mosip_prereg` (requêtes en lecture, comptages seuls) :
- `appointment_date` vaut 31/12/9999 pour tous les rendez-vous (actifs et consommés) : aucune expiration possible,
  « Expirées » restera à 0 ; seul `booking_dtimes` est exploitable.
- 444 pré-inscriptions ont plusieurs lignes de rendez-vous, toujours pour le même centre (double envoi en mai 2025,
  re-réservation encore active en septembre 2026) ; compter en `count(distinct prereg_id)`.
- 2 245 rendez-vous sans pré-inscription ; 1 144 pré-inscriptions « Pending_Appointment » avec rendez-vous et 268
  « Booked » sans rendez-vous.
- Pas de statut `Expired` ni `Cancelled` ; tables de copie présentes (`applicant_demographic_consumed_16102025`,
  `asi_app`, `asi_doc`) à exclure de la capture.

## Travail par couche

### 1. Données (`data-engineer`)
- Migration `V3__page_enrolement.sql` (ajout seulement) :
  - `bi.fait_niu_jour` (jour de génération × centre × type de demande : NIU générés) — si P2 = flux ;
  - `bi.fait_preinscription_jour` (jour de création × statut regroupé : demandes, consommées), national ;
  - `bi.fait_rdv_jour` (jour de réservation × centre : rendez-vous réservés, honorés).
- `R__donnees_dev.sql` : préfectures des six régions, centres fictifs (« Centre n° … »), et environ 15 mois de
  lignes générées en SQL (`generate_series`, aléa déterministe) dans `fait_enrolement_jour`, `fait_niu_jour`,
  `fait_preinscription_jour`, `fait_rdv_jour`. Contrôle respecté : NIU + rejetées + échouées + en cours = inscriptions ;
  sexe `I` et tranche `inconnu` partout.
- Pas de job Spark dans ce lot : ces tables ne sont remplies qu'en `dev` (alimentation réelle : lots A et B).

### 2. API (`dev-backend`)
Toutes en lecture de la base BI, paramètres `du`, `au`, `region` (code de `bi.zone`), portée Keycloak appliquée par
`PorteeUtilisateur` (un `bi-regional` ne voit que sa région, quelle que soit la demande).

| Endpoint | Réponse |
|---|---|
| `GET /api/v1/enrolement/preinscription` | demandes, rendez-vous réservés, en attente, expirées, honorées, dernière demande ; `null` si indisponible |
| `GET /api/v1/enrolement/semaines` | 12 dernières semaines complètes de la période : inscriptions, NIU générés |
| `GET /api/v1/enrolement/territoire` | régions (ou préfectures de la région filtrée) : inscriptions, NIU, rejetées, échouées, en cours, délai médian (`null` jusqu'à `bi.fait_delai_niu_mois`) |
| `GET /api/v1/enrolement/centres?classement=inscriptions\|echecs\|rejets` | 5 premiers centres de la portée |

Tests : contrôleur (MockMvc) et intégration (Testcontainers) sur les chiffres de démonstration, dont la concordance
territoire = total national.

### 3. Front (`dev-front`)
- Filtre Région dans le bandeau (React Aria `Select`), porté par l'adresse (`filtresUrl.ts` : `region`), sur Vue
  d'ensemble, Enrôlement et Impression des cartes ; pastille « Ensemble du Togo » sur les blocs qui ne le suivent pas.
- Blocs, un fichier `.tsx` + CSS + test chacun : `BlocPreinscription`, `BlocSemaines` (ECharts barres + courbe,
  lecture de la semaine et tableau équivalent), `BlocTerritoire` (carte ECharts des régions et préfectures, contours
  OpenStreetMap / geoBoundaries de la maquette, tableau des zones, alerte ▲ rejets ≥ 3,5 %), `BlocAgeSexe` (« non
  disponible »), `BlocTopCentres` (onglets React Aria).
- Hooks TanStack Query dans `src/api/enrolement.ts`, types régénérés (`npm run api:types`).
- Formats uniquement via `lib/format.ts`, couleurs uniquement via `jetons.css`.

### 4. Vérification (`qa-testeur`, puis revues)
- `npm run lint && npm run typecheck && npm test` ; `mvn verify` ; `npm run test:e2e` (axe, captures 1 440 / 1 000 /
  390 px) et `/verif-visuelle` contre `maquette/captures/Enrolement-*.png`.
- Revues `auditeur-donnees` (concordance des chiffres), `expert-uiux`, `relecteur-securite` (portée régionale, aucune
  donnée nominative).

## Limites de l'environnement de Claude

Ni Maven ni Docker dans l'environnement de Claude : le SQL (migration et données de démonstration) est testé sur un
PostgreSQL 16 local, le front par lint, types et tests unitaires ; `mvn verify`, la génération de `schema.ts` (backend
démarré) et les tests Playwright sont à lancer sur le poste de l'équipe.

## Avancement (19/10/2026)
- Fait : migration `V3__niu_par_jour_de_generation.sql` (`bi.fait_niu_jour` seulement : les tables de pré-inscription
  attendent P1) ; préfectures dans `R__donnees_dev.sql` (centres du simulateur rattachés à une préfecture) ; volumes
  fictifs dans un profil `demo` séparé (`db/demo`, voir `docs/decisions.md`) au lieu de `R__donnees_dev.sql` ; API
  `semaines`, `territoire`, `centres` et `meta/regions` (paramètre `zone`, comme `devenir`) ; filtre Région ; blocs
  Semaines, Territoire, Âge et sexe, Top des centres ; tests unitaires, d'intégration et Playwright.
- Vérifié par Claude : SQL (migrations, données de démonstration, requêtes des repositories) sur PostgreSQL 16 ;
  front : lint, types, 42 tests unitaires, build, 18 parcours Playwright avec axe aux trois largeurs ; Java vérifié
  seulement contre des bouchons d'API (pas de Maven dans son environnement).
- À lancer sur le poste : `mvn verify`, `npm run api:types` (backend démarré) puis `npm run typecheck`,
  `/verif-visuelle`.
- Reste : bloc Pré-inscription (P1).
