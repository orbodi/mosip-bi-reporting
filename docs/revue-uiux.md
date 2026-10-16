# Revue UI/UX générale de la maquette BI ANID (9 oct. 2026)

Revue faite par un agent « expert UI/UX » sur les 7 pages (Vue d'ensemble, Enrôlement, Impression des cartes, ABIS, IDPS, Authentifications, Exploration) à 1 440, 1 000 et 390 px. Axes : cohérence visuelle, ergonomie et lisibilité, mobile et tablette, accessibilité (WCAG 2.1 AA). Constats bloquants vérifiés dans les sources ; contrastes recalculés. Aucune correction faite : en attente de validation.

## Verdict
Maquette avancée, gabarit tenu sur les 7 pages, bonnes bases d'accessibilité (lang, aria-current, rôles table et img, focus visible). Pas encore prête à être figée : chiffres qui se contredisent entre pages, portée des filtres trompeuse, design system à consolider (21 tailles de police, 58 couleurs en dur, 5 styles de tableau).

## Bloquants
- UX-01 Chiffres incohérents entre pages : NIU par région de la Vue d'ensemble différents de l'Enrôlement (Grand Lomé 961 080 contre 961 808 ; total 3 054 976 au lieu de 3 058 886) ; demandes d'impression 3 113 431 supérieures aux NIU 3 058 886 sans explication ; Top des centres avec plus de cartes expédiées que d'inscriptions (EPP Doumassesse 44 370 contre 43 534).
- UX-02 Dates : « dernier rejet le 13/03/2026 » (Cartes) après la mise à jour du 14/01/2026 ; IDPS au 03/07/2026 ; heures de mise à jour différentes selon la page (11h05 à 11h59).
- UX-03 Filtres du bandeau annoncés « appliqués à toute la page » : Région ne change qu'un panneau, Période ne change rien, la sélection revient à « Toutes ».
- UX-06 Contrastes sous 4,5:1 : zéros IDPS #9AA7B5 (2,45:1) ; libellés blancs des chevrons du parcours sur #2A78D6 (4,42:1) ; numéros d'étape (3,07:1).
- UX-07 Tableaux à 390 px : chevauchements dans le Top des centres (Cartes), en-têtes superposés (Enrôlement, IDPS), colonne clé masquée sans indice (Vue d'ensemble).
- UX-05 Listes déroulantes de l'Exploration non pilotables au clavier (flèches, Échap).
- UX-04 Focus clavier perdu au re-rendu : mesuré dans le simulateur qui reconstruit toute la page ; à garantir au développement.

## Importants
- UX-08/09 Mobile : 2 liens de navigation visibles sur 7, sans indice de défilement ; bandeau à hauteur fixe dont les filtres débordent. Pistes : bouton Menu, bouton « Filtres (n) ».
- UX-10 Graphiques hebdomadaires mobiles ouverts sur les semaines les plus anciennes.
- UX-11 Pourcentages en vedette (54,0 %, 100 %…) : nombre d'abord, % en complément (garder le taux d'exploitabilité par doigt, demandé).
- UX-12 Doublons : 215 736 affiché 4 fois (Authentifications) ; légende ABIS et 3 cartes identiques ; IDPS 6 cartes et 39 semaines pour 14 ordres.
- UX-15 Alertes portées par la couleur seule ; triangle jaune 1,83:1 ; Enrôlement : seuil en taux mais colonne en volumes.
- UX-16 Libellés et dénominateurs divergents (livrées/remises, Genre/Sexe, Depuis le début/Toute la période, 54,0 % des inscrits contre 57,1 % des expédiées).
- UX-19 Bordures des champs (1,36:1) et des pilules du bandeau (2,19:1) sous 3:1.
- UX-20 à 23 Design system : 21 tailles de police, 58 couleurs (18 gris proches, 2 jaunes), même vert pour NIU et Hommes, 5 variantes de tableau.
- UX-24 Tablette 1 000 px : tout passe en une colonne (+51 % de hauteur).
- UX-25 États vide, chargement, erreur non spécifiés.
- UX-17/18 Exploration : niveaux grisés « — » sans aide visible, tableau de 2 colonnes étiré sur 1 248 px, onglets sans navigation aux flèches.
- UX-14 ABIS : jauges sur échelles différentes (255, 100, 255).

## Mineurs (UX-26 à 36)
Coins jaunes pas au même endroit ; valeurs KPI désalignées quand le titre passe sur 2 lignes ; ratios de colonnes variables ; ordre des régions variable ; règles d'étiquettes d'axe différentes ; 14 rayons et 7 ombres ; pas de lien « Aller au contenu » ; cibles tactiles sous 44 px ; informations seulement en infobulle (ABIS) ; CSS mort ; ordre Femmes/Hommes inversé.

## Écartés ou nuancés après vérification
- « Il faut cliquer Valider pour appliquer les indicateurs » : faux, les choix s'appliquent au clic.
- Revenir à Visage / Empreintes / Œil droit et traduire HIT / NO HIT : contraire aux choix du client (libellés du document IN Groupe). Seule piste gardée : noms de journaux techniques en mention « Source ».
- Graphique au-dessus du tableau d'Exploration : retiré à la demande du client.

## À décider avant le développement
1. Source de données unique et dictionnaire des indicateurs (définition, dénominateur, libellé, fraîcheur par source).
2. Portée des filtres et affichage de l'état filtré.
3. Échelle typographique (7 tailles + 2 tailles de KPI).
4. Jetons de couleur (neutres, marque, sémantiques, data-viz, couleur fixe par indicateur).
5. Un seul composant Tableau (total, région cliquable, ordre, mobile).
6. Patron KPI (nombre avant %, composant Alerte avec seuil).
7. Interactions (onglets, listes, carte) et leur modèle clavier.
8. Responsive (2 colonnes jusqu'à 900 px, menu et filtres mobiles).

## Corrections appliquées (9 oct. 2026, version 89 de l'artefact)
Couche build/p_fix.py appliquée après les constructeurs (remplacements vérifiés + feuille commune), plus quelques textes corrigés dans les constructeurs (sauvegardes *_v87.py).
- Chiffres et dates (UX-01, UX-02) : NIU par région de la Vue d'ensemble alignés sur l'Enrôlement (total 3 058 886) ; « Paquets traités » = 3 154 600 (NIU + échoués + rejetés) ; anomalies réelles du BI signalées sans modifier les valeurs (demandes d'impression : « 54 545 de plus que les NIU : à réconcilier » ; rejet daté du 13/03/2026 « à vérifier » ; note sous le Top des centres sur les centres qui ont plus de cartes expédiées que d'inscriptions) ; axe IDPS arrêté à la semaine de la mise à jour (semaine 27).
- Filtres (UX-03) : les filtres sans effet sont retirés des bandeaux (Période partout ; Demande, Genre, Âge ; Type d'erreur ; Type, Partenaire ; Région sur IDPS et Authentifications). Région reste sur Vue d'ensemble (désormais reliée à la carte), Enrôlement et Impression des cartes ; quand une région est choisie, les blocs qui ne la suivent pas portent la pastille « Ensemble du Togo ». Lien « Filtres détaillés dans l'Exploration » dans chaque bandeau.
- Accessibilité (UX-05, 06, 15, 18, 19, 32) : chevrons du parcours en #2368C2 et numéros sur pastille blanche ; zéros IDPS en #4B5A6E ; triangles d'alerte en #B07D00 avec légende du seuil (rejet ≥ 3,5 %, plus de la moitié à remettre, échec ≥ 50 %) et taux affiché à côté des rejets signalés ; contours des pilules et des champs renforcés ; listes de l'Exploration au clavier (↓ ouvre, ↑ ↓ Début Fin, Entrée, Échap rend le focus), onglets aux flèches avec tabulation itinérante ; lien « Aller au contenu ».
- Mobile et tablette (UX-07 à 10, 24, 33) : menu « Menu » et avatar seul sous 700 px ; bandeau qui suit son contenu ; tableaux réduits aux colonnes clés sur téléphone ; Top des centres empilé ; graphiques hebdomadaires calés sur la semaine la plus récente ; paires de panneaux côte à côte jusqu'à 900 px (graphique de l'Enrôlement fluide, une date sur deux) ; champs de 44 px dans l'Exploration.
- Lisibilité (UX-11, 12, 13, 16, 22, 36) : héros de la Vue d'ensemble en nombre (1 770 796 cartes en main, soit 54,0 %) ; doublons retirés (légendes sans nombres sur ABIS et Authentifications, panneau « Partenaires raccordés » retiré, IDPS à 3 cartes) ; sources techniques ABIS en mention « Source » ; codes BIO/OTP/DEMO/MULTIPLE en note ; « Cartes livrées » devient « Cartes remises » ; IDPS explique son périmètre (pilote, distinct des 3 101 590 cartes) ; NIU en marine dans le graphique hebdomadaire, hommes en vert #0E8A62 ; femmes avant hommes ; « Honorées à l'inscription » en « — » avec explication ; unité « inscriptions » non répétée.
Non repris, à trancher pendant la structuration : jetons de couleur, échelle typographique, composant Tableau unique, rayons et ombres (UX-20, 21, 23, 31) ; échelles de score ABIS (UX-14) ; décors et ratios de grilles (UX-26, 28) ; états vide/chargement/erreur à spécifier (UX-25). Contrôles : aucune erreur JS, aucun débordement horizontal aux trois largeurs, aucun texte sous 4,5:1 (hors faux positifs du bandeau).
