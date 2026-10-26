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
    // La colonne des noms porte le niveau des lignes.
    expect(tableau.getByRole('columnheader', { name: 'Région' })).toBeInTheDocument();
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
    expect(routeur.state.location.search).toMatchObject({ zone: 'SAV' });
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
    await waitFor(() => expect(routeur.state.location.search).not.toHaveProperty('zone'));
  });

  it('descend jusqu’aux communes : fil d’Ariane, tri par inscriptions, zones vides omises, carte de la région', async () => {
    const appels = simulerApi();
    const routeur = afficher('/enrolement?zone=SAV');
    const utilisateur = userEvent.setup();

    const prefectures = within(
      await (await blocAffiche()).findByRole('table', { name: 'Préfectures de la région Savanes' }),
    );
    await utilisateur.click(prefectures.getByRole('button', { name: /Tône/ }));

    expect(await screen.findByRole('heading', { name: 'Territoire : préfecture Tône' })).toBeInTheDocument();
    expect(routeur.state.location.search).toMatchObject({ zone: 'SAV-02' });
    const fil = within(bloc().getByRole('navigation', { name: 'Fil d’Ariane du territoire' }));
    expect(fil.getByRole('button', { name: 'Togo' })).toBeInTheDocument();
    expect(fil.getByRole('button', { name: 'Savanes' })).toBeInTheDocument();
    expect(fil.getByText('Tône')).toHaveAttribute('aria-current', 'location');

    const communes = within(bloc().getByRole('table', { name: 'Communes de la préfecture Tône' }));
    // Triées par inscriptions ; « Tône 3 », sans inscription, n'est pas affichée mais comptée.
    expect(communes.getAllByRole('rowheader').map((c) => c.textContent)).toEqual(['Tône 2', 'Tône 1']);
    expect(communes.getByRole('columnheader', { name: 'Commune' })).toBeInTheDocument();
    expect(bloc().getByText(/Le tableau omet 1 commune sans inscription sur la période/)).toBeInTheDocument();
    // Pas de colonne Pré-inscriptions sous la préfecture : elles ne sont situées qu'à la préfecture.
    expect(communes.queryByRole('columnheader', { name: 'Pré-inscriptions' })).not.toBeInTheDocument();
    // Carte de contexte : la région Savanes, préfecture Tône mise en évidence.
    expect(
      await (
        await blocAffiche()
      ).findByRole('img', { name: /Carte de la région Savanes : préfecture Tône mise en évidence/ }),
    ).toBeInTheDocument();
    expect(
      appels.some((u) => u.pathname.endsWith('/territoire') && u.searchParams.get('zone') === 'SAV-02'),
    ).toBe(true);

    await utilisateur.click(fil.getByRole('button', { name: 'Savanes' }));
    expect(await screen.findByRole('heading', { name: 'Territoire : région Savanes' })).toBeInTheDocument();
    expect(routeur.state.location.search).toMatchObject({ zone: 'SAV' });
  });

  it('un canton mêle une localité et un centre rattaché directement : le centre ne s’ouvre pas', async () => {
    simulerApi();
    afficher('/enrolement?zone=SAV-02-K1');

    const tableau = within(
      await (await blocAffiche()).findByRole('table', { name: 'Sous-zones du canton Canton de Nano' }),
    );
    expect(
      await screen.findByRole('heading', { name: 'Territoire : canton Canton de Nano' }),
    ).toBeInTheDocument();
    expect(tableau.getByRole('button', { name: /Nano/ })).toBeInTheDocument();
    expect(tableau.queryByRole('button', { name: /EPP Nano/ })).not.toBeInTheDocument();
    expect(tableau.getByText('(centre)')).toBeInTheDocument();
    expect(tableau.getByRole('columnheader', { name: 'Zone' })).toBeInTheDocument();
    const fil = within(bloc().getByRole('navigation', { name: 'Fil d’Ariane du territoire' }));
    expect(fil.getAllByRole('button').map((b) => b.textContent)).toEqual([
      'Togo',
      'Savanes',
      'Tône',
      'Tône 2',
    ]);
  });

  it('pagine les longues listes : 20 lignes par défaut, puis 10, pages numérotées', async () => {
    simulerApi();
    afficher('/enrolement?zone=SAV-02-K2');
    const utilisateur = userEvent.setup();

    const tableau = within(
      await (await blocAffiche()).findByRole('table', { name: 'Localités du canton Canton de Dapaong' }),
    );
    expect(tableau.getAllByRole('rowheader')).toHaveLength(20);
    expect(bloc().getByText(/^1–20 sur 25 localités$/)).toBeInTheDocument();
    const pages = within(bloc().getByRole('navigation', { name: 'Pages du tableau des localités' }));
    expect(pages.getByRole('button', { name: 'Page précédente' })).toBeDisabled();
    expect(pages.getByRole('button', { name: 'Page 1' })).toHaveAttribute('aria-current', 'page');

    await utilisateur.click(pages.getByRole('button', { name: 'Page 2' }));
    expect(tableau.getAllByRole('rowheader').map((c) => c.textContent)).toEqual([
      'Localité 21',
      'Localité 22',
      'Localité 23',
      'Localité 24',
      'Localité 25',
    ]);
    expect(bloc().getByText(/^21–25 sur 25 localités$/)).toBeInTheDocument();

    await utilisateur.click(bloc().getByRole('button', { name: '10 lignes par page' }));
    expect(tableau.getAllByRole('rowheader')).toHaveLength(10);
    expect(bloc().getByText(/^1–10 sur 25 localités$/)).toBeInTheDocument();
    expect(pages.getByRole('button', { name: 'Page 3' })).toBeInTheDocument();
  });

  it('un ancien lien ?region= ouvre toujours la région', async () => {
    simulerApi();
    afficher('/enrolement?region=SAV');
    expect(await screen.findByRole('heading', { name: 'Territoire : région Savanes' })).toBeInTheDocument();
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
