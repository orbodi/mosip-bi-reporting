import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createMemoryHistory } from '@tanstack/react-router';
import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { DevenirInscriptions } from '../../api/client';
import { RAFRAICHISSEMENT_MS } from '../../api/client';
import { nf, pct } from '../../lib/format';
import { creerRouteur } from '../../routeur';

const META = {
  application: 'BI Reporting ANID',
  sources: [
    {
      source: 'enrolement',
      libelle: 'Enrôlement',
      premiereDonnee: '2026-08-17',
      derniereDonnee: '2026-10-16T10:42:00Z',
    },
  ],
};

const DEVENIR: DevenirInscriptions = {
  perimetre: 'Ensemble du Togo',
  inscriptions: 1000,
  niuGeneres: 933,
  enCours: 40,
  echouees: 1,
  rejetees: 26,
  nonClassees: 0,
};

/** Réponses successives de l'API pour /enrolement/devenir ; /meta répond toujours META. */
function simulerApi(...reponses: DevenirInscriptions[]) {
  const appels: string[] = [];
  let n = 0;
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: URL) => {
      appels.push(url.toString());
      const corps = url.pathname.endsWith('/meta') ? META : reponses[Math.min(n++, reponses.length - 1)];
      return new Response(JSON.stringify(corps), { headers: { 'Content-Type': 'application/json' } });
    }),
  );
  return appels;
}

function afficher(adresse: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <RouterProvider router={creerRouteur(createMemoryHistory({ initialEntries: [adresse] }))} />
    </QueryClientProvider>,
  );
}

describe('Devenir des inscriptions', () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it('affiche les NIU générés d’abord, puis les quatre statuts avec leur part', async () => {
    simulerApi(DEVENIR);
    afficher('/enrolement');

    // Testing Library ramène les espaces fines et insécables à des espaces simples avant de comparer.
    const sousTitre = `NIU générés, soit ${pct(0.933)} des ${nf(1000)} inscriptions`.replace(/\s+/g, ' ');
    expect(await screen.findByText(sousTitre)).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: 'Devenir des inscriptions' })).toBeInTheDocument();
    expect(screen.getByText('Ensemble du Togo')).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /NIU générés 93,3/ })).toBeInTheDocument();
    for (const libelle of ['En cours', 'Échoués', 'Rejetés']) {
      expect(screen.getByText(libelle)).toBeInTheDocument();
    }
    expect(screen.queryByText('Non classés')).not.toBeInTheDocument();
  });

  it('signale les inscriptions non classées sans les répartir', async () => {
    simulerApi({ ...DEVENIR, niuGeneres: 900, nonClassees: 33 });
    afficher('/enrolement');

    expect(await screen.findByText('Non classés')).toBeInTheDocument();
    expect(screen.getByRole('note')).toHaveTextContent('sans correspondance validée');
  });

  it('envoie la plage du filtre Période à l’API', async () => {
    const appels = simulerApi(DEVENIR);
    afficher('/enrolement?periode=7j');

    await screen.findByText('Rejetés');
    expect(appels.some((u) => u.includes('/enrolement/devenir?du=2026-10-10&au=2026-10-16'))).toBe(true);
  });

  it('se met à jour seul toutes les 30 secondes (pipeline temps réel)', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    simulerApi(DEVENIR, { ...DEVENIR, inscriptions: 1001, enCours: 41 });
    afficher('/enrolement');
    expect(await screen.findByText(nf(40))).toBeInTheDocument();

    await vi.advanceTimersByTimeAsync(RAFRAICHISSEMENT_MS + 100);
    expect(await screen.findByText(nf(41))).toBeInTheDocument();
  });
});
