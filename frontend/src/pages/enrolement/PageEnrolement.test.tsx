import { screen, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { AGE_SEXE, afficher, PREINSCRIPTIONS, simulerApi } from '../../test/apiSimulee';

const TRANCHES = ['60 ans et +', '46 à 60', '36 à 45', '26 à 35', '19 à 25', '15 à 18', '6 à 14', '0 à 5'];
const texte = (t: string) => t.replace(/\s+/g, ' ');

describe('Page Enrôlement', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('présente les six blocs dans l’ordre de la maquette', async () => {
    simulerApi();
    afficher('/enrolement');

    await screen.findByRole('heading', { name: 'Territoire : vue nationale' });
    expect(screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent)).toEqual([
      'Pré-inscription',
      'Devenir des inscriptions',
      'Inscriptions et NIU par semaine',
      'Territoire : vue nationale',
      'NIU générés par âge et par sexe',
      'Top des centres',
    ]);
  });

  it('pré-inscription : chiffres de l’API, dernière demande, sexe à 0 faute de source', async () => {
    simulerApi();
    afficher('/enrolement');

    const pre = within(await screen.findByRole('region', { name: 'Pré-inscription' }));
    expect(await pre.findByText(texte('606 850'))).toBeInTheDocument();
    expect(pre.getByText(texte('546 964'))).toBeInTheDocument();
    expect(pre.getByText('14/01/2026')).toBeInTheDocument();
    expect(pre.getByText('à 11h28')).toBeInTheDocument();
    expect(pre.getByText('Femmes pré-inscrites')).toBeInTheDocument();
    expect(pre.getByText('Hommes pré-inscrits')).toBeInTheDocument();
    expect(pre.queryByText('Expirées')).not.toBeInTheDocument();
    expect(pre.queryByText(/Honorées/)).not.toBeInTheDocument();
    expect(pre.queryByRole('note')).not.toBeInTheDocument();
    expect(screen.queryByText(/pas encore raccordée|non disponible|non mesuré/i)).not.toBeInTheDocument();
  });

  it('pré-inscription : femmes et hommes parmi les sexes connus, note pour les autres', async () => {
    simulerApi({ '/enrolement/preinscriptions': { ...PREINSCRIPTIONS, femmes: 300000, hommes: 200000 } });
    afficher('/enrolement');

    const pre = within(await screen.findByRole('region', { name: 'Pré-inscription' }));
    expect(await pre.findByText(texte('300 000'))).toBeInTheDocument();
    expect(pre.getByText(texte('200 000'))).toBeInTheDocument();
    expect(pre.getByText(texte('60,0 % des sexes connus'))).toBeInTheDocument();
    expect(pre.getByText(texte('40,0 % des sexes connus'))).toBeInTheDocument();
    expect(pre.getByRole('note').textContent).toMatch(/^Sexe connu pour 500\s000 demandes sur 606\s850/);
  });

  it('âge et sexe : pyramide de l’API pour la région choisie', async () => {
    const appels = simulerApi();
    afficher('/enrolement?region=SAV');

    const bloc = within(await screen.findByRole('region', { name: 'NIU générés par âge et par sexe' }));
    expect(await bloc.findByText(/Région Savanes/)).toBeInTheDocument();
    const pyramide = within(
      bloc.getByRole('table', { name: 'Répartition des NIU par tranche d’âge et par sexe' }),
    );
    expect(pyramide.getAllByRole('rowheader').map((t) => t.textContent)).toEqual(TRANCHES);
    // 26 à 35 ans en Savanes (14 % des chiffres nationaux de la simulation) : 53 959 femmes, 47 535 hommes.
    expect(await pyramide.findByText(texte('53 959'))).toBeInTheDocument();
    expect(pyramide.getByText(texte('47 535'))).toBeInTheDocument();
    expect(
      appels.some((u) => u.pathname.endsWith('/enrolement/age-sexe') && u.searchParams.get('zone') === 'SAV'),
    ).toBe(true);
    const section = screen.getByRole('region', { name: 'NIU générés par âge et par sexe' });
    expect(section.querySelectorAll('.pyramide__barre--femmes, .pyramide__barre--hommes')).toHaveLength(18);
  });

  it('âge et sexe sans données : huit tranches à 0, barres vides, sans note', async () => {
    simulerApi({
      '/enrolement/age-sexe': {
        ...AGE_SEXE,
        disponible: false,
        nonRenseignes: null,
        tranches: AGE_SEXE.tranches.map((t) => ({ tranche: t.tranche, femmes: null, hommes: null })),
      },
    });
    afficher('/enrolement');

    const bloc = within(await screen.findByRole('region', { name: 'NIU générés par âge et par sexe' }));
    expect(bloc.queryByRole('note')).not.toBeInTheDocument();
    const pyramide = within(
      bloc.getByRole('table', { name: 'Répartition des NIU par tranche d’âge et par sexe' }),
    );
    expect(pyramide.getAllByRole('rowheader').map((t) => t.textContent)).toEqual(TRANCHES);
    expect(pyramide.getAllByRole('cell').every((c) => c.textContent === '0')).toBe(true);
    expect(bloc.getByText(/^Femmes :/).textContent).toMatch(/^Femmes : 0 \(0,0\s%\)$/);
    // Seules les puces de la légende sont colorées : aucune barre n'est dessinée.
    const section = screen.getByRole('region', { name: 'NIU générés par âge et par sexe' });
    expect(section.querySelectorAll('.pyramide__barre--femmes, .pyramide__barre--hommes')).toHaveLength(2);
  });

  it('mène aux filtres détaillés de l’Exploration', async () => {
    simulerApi();
    afficher('/enrolement');

    expect(await screen.findByRole('link', { name: /Filtres détaillés dans l’Exploration/ })).toHaveAttribute(
      'href',
      '/exploration',
    );
  });
});
