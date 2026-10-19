import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createMemoryHistory } from '@tanstack/react-router';
import { render, screen, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { creerRouteur } from '../../routeur';

const META = {
  application: 'BI Reporting ANID',
  sources: [
    {
      source: 'enrolement',
      libelle: 'Enrôlement',
      premiereDonnee: '2024-01-01',
      derniereDonnee: '2026-01-14T11:42:00Z',
    },
    {
      source: 'cartes',
      libelle: 'Impression des cartes',
      premiereDonnee: '2024-02-01',
      derniereDonnee: '2026-01-14T11:59:00Z',
    },
    { source: 'idps', libelle: 'IDPS', premiereDonnee: '2026-07-03', derniereDonnee: '2026-07-03T17:09:00Z' },
  ],
};

function afficher(adresse: string) {
  const routeur = creerRouteur(createMemoryHistory({ initialEntries: [adresse] }));
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <RouterProvider router={routeur} />
    </QueryClientProvider>,
  );
}

describe('Coque', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      // /meta seulement : les blocs des pages reçoivent une erreur 404 (ils ont leurs propres tests).
      vi.fn(async (url: URL) =>
        url.pathname.endsWith('/meta')
          ? new Response(JSON.stringify(META), { headers: { 'Content-Type': 'application/json' } })
          : new Response('', { status: 404 }),
      ),
    );
  });
  afterEach(() => vi.unstubAllGlobals());

  it('affiche les 7 onglets et marque la page courante', async () => {
    afficher('/enrolement');
    const nav = (await screen.findAllByRole('navigation', { name: 'Sections du tableau de bord' }))[0];
    const liens = within(nav).getAllByRole('link');
    expect(liens.map((l) => l.textContent)).toEqual([
      'Vue d’ensemble',
      'Enrôlement',
      'Impression des cartes',
      'ABIS',
      'IDPS',
      'Authentifications',
      'Exploration',
    ]);
    expect(within(nav).getByRole('link', { name: 'Enrôlement' })).toHaveAttribute('aria-current', 'page');
  });

  it('affiche le titre et la date de mise à jour de la source de la page', async () => {
    afficher('/idps');
    expect(await screen.findByRole('heading', { level: 1, name: 'IDPS' })).toBeInTheDocument();
    expect(await screen.findByText('Dernière mise à jour : 03/07/2026 à 17h09')).toBeInTheDocument();
  });

  it('calcule la plage d’une période relative depuis l’adresse', async () => {
    afficher('/enrolement?periode=7j');
    expect(await screen.findByText('Du 08/01/2026 au 14/01/2026')).toBeInTheDocument();
  });
});
