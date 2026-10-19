# Frontend (React)

React 19, TypeScript strict, Vite. Application monopage derrière Keycloak.

## Organisation

- `src/routeur.tsx` : routes (TanStack Router, déclarées en code) ; les filtres communs sont validés par `lib/filtresUrl.ts`.
- `src/pages/` : une page par onglet ; `pages.ts` liste les onglets, leur source et leur page de maquette.
- `src/composants/` : composants partagés (`coque/` : en-tête, bandeau, filtre Période, pastille de mise à jour, pied).
  Un composant = un fichier `.tsx`, son CSS à côté, son test `*.test.tsx` à côté.
- `src/api/` : `client.ts` (appel avec jeton), un fichier de hooks TanStack Query par domaine, `schema.ts` généré.
- `src/lib/` : logique pure testée (formats, périodes). Toute règle de calcul ou d'affichage va ici, avec un test.
- `src/composants/graphique/` : enveloppe ECharts (`Graphique.tsx`, ECharts chargé à la demande) ;
  `src/composants/carte/` : contours du Togo (maquette) et fonds de carte SVG.
- `src/test/apiSimulee.tsx` : API simulée et rendu de l'application pour les tests des pages.
- `src/styles/jetons.css` : seules couleurs, tailles, rayons et ombres autorisés.

## Conventions

- Textes de l'interface en français, libellés exacts de la maquette ; formats via `lib/format.ts` (jamais `toLocaleString` direct).
- Données : `useQuery` avec une clé `[domaine, ressource, filtres]` ; jamais de `fetch` dans un composant.
- Types de l'API : uniquement depuis `src/api/schema.ts` (`npm run api:types` après un changement du backend).
- Filtres de page dans l'adresse (`useSearch` / `navigate({ search })`), pas dans un état local.
- Composants interactifs (listes, onglets, menus, dates) : React Aria Components, pour le clavier et les lecteurs d'écran.
- Graphiques : Apache ECharts (import modulaire `echarts/core`), couleurs des jetons data-viz ; chaque graphique a un
  titre, une légende lisible et un équivalent texte ou tableau.
- Pas de nouvelle dépendance sans raison écrite dans `docs/decisions.md`.

## Vérifier

- `npm run lint && npm run typecheck && npm test` à chaque changement (le hook Stop le fait).
- `npm run test:e2e` quand une page ou la coque change : parcours, axe (aucune violation WCAG AA) et captures
  aux trois largeurs dans le rapport Playwright, à comparer avec `maquette/captures/` (skill `/verif-visuelle`).
