import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { afficher, simulerApi } from '../test/apiSimulee';

describe('Pages de la maquette', () => {
  afterEach(() => vi.unstubAllGlobals());

  it.each([
    ['/impression-cartes', 'Impression et remise'],
    ['/abis', 'Transactions ABIS'],
    ['/idps', 'Ordres d’impression'],
    ['/authentifications', 'Requêtes d’authentification'],
  ])('%s : mise en page de la maquette, indicateurs à 0, sans note de source', async (chemin, bloc) => {
    simulerApi();
    afficher(chemin);

    const premier = within(await screen.findByRole('region', { name: bloc }));
    expect(premier.getAllByText('0').length).toBeGreaterThanOrEqual(2);
    expect(premier.queryByText('–')).not.toBeInTheDocument();
    expect(screen.queryByText(/pas encore raccordée|non disponible|indisponible/i)).not.toBeInTheDocument();
  });

  it('Vue d’ensemble : étapes d’enrôlement de l’API, autres étapes à 0', async () => {
    simulerApi();
    afficher('/');

    const parcours = within(
      await screen.findByRole('region', { name: 'De la pré-inscription à la carte en main' }),
    );
    expect(await parcours.findByText('3 278 239'.replace(/\s/g, ' '))).toBeInTheDocument();
    expect(parcours.getByText('Pré-inscriptions')).toBeInTheDocument();
    const regions = within(screen.getByRole('region', { name: 'Le parcours par région' }));
    expect(await regions.findByRole('rowheader', { name: 'Grand Lomé' })).toBeInTheDocument();
  });

  it('Exploration : inscriptions par région depuis l’API, puis par préfecture de la région choisie', async () => {
    const appels = simulerApi();
    afficher('/exploration');
    const utilisateur = userEvent.setup();

    const resultat = within(await screen.findByRole('region', { name: 'Inscriptions par région' }));
    await utilisateur.click(await resultat.findByRole('button', { name: /Savanes/ }));
    expect(
      await screen.findByRole('heading', { level: 2, name: 'Inscriptions par préfecture' }),
    ).toBeInTheDocument();
    expect(
      appels.some((u) => u.pathname.endsWith('/territoire') && u.searchParams.get('zone') === 'SAV'),
    ).toBe(true);
    expect(await screen.findByRole('rowheader', { name: 'Tône' })).toBeInTheDocument();
  });
});
