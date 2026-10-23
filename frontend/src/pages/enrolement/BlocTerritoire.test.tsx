import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { afficher, simulerApi } from '../../test/apiSimulee';

const bloc = () => within(screen.getByRole('region', { name: /^Territoire/ }));
const blocAffiche = async () => within(await screen.findByRole('region', { name: /^Territoire/ }));

describe('Territoire', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('vue nationale : une ligne par région, chiffres de la zone et alerte de rejet', async () => {
    simulerApi();
    afficher('/enrolement');

    expect(
      await screen.findByRole('heading', { level: 2, name: 'Territoire : vue nationale' }),
    ).toBeInTheDocument();
    const tableau = within(await (await blocAffiche()).findByRole('table', { name: 'Régions' }));
    const lignes = tableau.getAllByRole('row').slice(1);
    expect(lignes.map((l) => within(l).getByRole('rowheader').textContent)).toEqual([
      'Savanes',
      'Kara',
      'Centrale',
      'Plateaux',
      'Maritime',
      'Grand Lomé',
    ]);
    // Pré-inscriptions, première colonne de chiffres (Savanes : 180 096 dans la simulation).
    expect(tableau.getByRole('columnheader', { name: 'Pré-inscriptions' })).toBeInTheDocument();
    expect(within(lignes[0]).getAllByRole('cell')[0].textContent?.replace(/\s/g, ' ')).toBe('180 096');
    // Savanes : 16 072 rejets sur 450 239 inscriptions = 3,6 % → ▲ (seuil 3,5 %).
    expect(within(lignes[0]).getByLabelText('Taux de rejet élevé')).toBeInTheDocument();
    expect(within(lignes[1]).queryByLabelText('Taux de rejet élevé')).not.toBeInTheDocument();
    expect(bloc().getByText('dans 6 régions')).toBeInTheDocument();
    expect(bloc().getByText(/Togo : 93,3/)).toBeInTheDocument();
  });

  it('un clic sur une région choisit cette région : préfectures, fil d’Ariane et adresse', async () => {
    const appels = simulerApi();
    const routeur = afficher('/enrolement');
    const utilisateur = userEvent.setup();

    const tableau = within(await (await blocAffiche()).findByRole('table', { name: 'Régions' }));
    await utilisateur.click(tableau.getByRole('button', { name: /Savanes/ }));

    expect(await screen.findByRole('heading', { name: 'Territoire : région Savanes' })).toBeInTheDocument();
    expect(routeur.state.location.search).toMatchObject({ region: 'SAV' });
    expect(
      appels.some((u) => u.pathname.endsWith('/territoire') && u.searchParams.get('zone') === 'SAV'),
    ).toBe(true);
    const prefectures = within(bloc().getByRole('table', { name: 'Préfectures de la région Savanes' }));
    expect(prefectures.getAllByRole('rowheader').map((c) => c.textContent)).toEqual([
      'Cinkassé',
      'Tône',
      'Kpendjal',
      'Tandjouaré',
      'Oti',
    ]);
    // Part du total national, calculée avec la vue nationale.
    expect(await (await blocAffiche()).findByText(/du total national/)).toBeInTheDocument();

    await utilisateur.click(bloc().getByRole('button', { name: 'Togo' }));
    expect(await screen.findByRole('heading', { name: 'Territoire : vue nationale' })).toBeInTheDocument();
    await waitFor(() => expect(routeur.state.location.search).not.toHaveProperty('region'));
  });

  it('sans réponse de l’API, garde la carte et le tableau des régions, chiffres à 0', async () => {
    simulerApi({ '/enrolement/territoire': undefined });
    afficher('/enrolement');

    const b = await blocAffiche();
    await waitFor(() => expect(b.queryByText('Chargement des chiffres…')).not.toBeInTheDocument());
    expect(b.queryByRole('alert')).not.toBeInTheDocument();
    const tableau = within(b.getByRole('table', { name: 'Régions' }));
    expect(tableau.getAllByRole('rowheader').map((c) => c.textContent)).toEqual([
      'Savanes',
      'Kara',
      'Centrale',
      'Plateaux',
      'Maritime',
      'Grand Lomé',
    ]);
    expect(tableau.queryByText('–')).not.toBeInTheDocument();
    expect(tableau.getAllByText('0').length).toBeGreaterThanOrEqual(6);
    expect(b.getByText(/^Togo : 0,0\s%\sde NIU générés, 0 inscriptions$/)).toBeInTheDocument();
    expect(b.getByRole('img', { name: /Carte des régions du Togo/ })).toBeInTheDocument();
  });
});
