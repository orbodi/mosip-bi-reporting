import { createRootRoute, createRoute, createRouter, type RouterHistory } from '@tanstack/react-router';
import type { ComponentType } from 'react';
import { Coque } from './composants/coque/Coque';
import { validerFiltres } from './lib/filtresUrl';
import { PageAConstruire } from './pages/PageAConstruire';
import { PageAbis } from './pages/abis/PageAbis';
import { PageAuthentifications } from './pages/authentifications/PageAuthentifications';
import { PageCartes } from './pages/cartes/PageCartes';
import { PageEnrolement } from './pages/enrolement/PageEnrolement';
import { PageExploration } from './pages/exploration/PageExploration';
import { PageIdps } from './pages/idps/PageIdps';
import { PageVueEnsemble } from './pages/vue-ensemble/PageVueEnsemble';
import { PAGES, type DefinitionPage } from './pages/pages';

/** Pages déjà construites ; les autres affichent la liste de leurs blocs à construire. */
const PAGES_CONSTRUITES: Partial<Record<DefinitionPage['chemin'], ComponentType<{ page: DefinitionPage }>>> =
  {
    '/': PageVueEnsemble,
    '/enrolement': PageEnrolement,
    '/impression-cartes': PageCartes,
    '/abis': PageAbis,
    '/idps': PageIdps,
    '/authentifications': PageAuthentifications,
    '/exploration': PageExploration,
  };

const racine = createRootRoute({
  component: Coque,
  validateSearch: validerFiltres,
});

const routesPages = PAGES.map((page) =>
  createRoute({
    getParentRoute: () => racine,
    path: page.chemin,
    component: () => {
      const Page = PAGES_CONSTRUITES[page.chemin] ?? PageAConstruire;
      return <Page page={page} />;
    },
  }),
);

const arbre = racine.addChildren(routesPages);

export function creerRouteur(history?: RouterHistory) {
  return createRouter({ routeTree: arbre, history, defaultPreload: 'intent' });
}

export const routeur = creerRouteur();

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof routeur;
  }
}
