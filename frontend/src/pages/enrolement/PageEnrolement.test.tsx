import { screen, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { AGE_SEXE, afficher, PREINSCRIPTIONS, simulerApi } from '../../test/apiSimulee';

const TRANCHES = ['60 ans et +', '46 à 60', '36 à 45', '26 à 35', '19 à 25', '15 à 18', '6 à 14', '0 à 5'];
const texte = (t: string) => t.replace(/\s+/g, ' ');

describe('Page Enrôlement', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('présente les sept blocs dans l’ordre de la maquette', async () => {
    simulerApi();
    afficher('/enrolement');

    await screen.findByRole('heading', { name: 'Territoire : vue nationale' });
    expect(screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent)).toEqual([
      'Pré-inscription',
      'Profil des pré-inscrits',
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

  it('dernière mise à jour : le rafraîchissement le plus récent de l’enrôlement et de la pré-inscription', async () => {
    simulerApi();
    afficher('/enrolement');

    expect(await screen.findByText('Dernière mise à jour : 14/01/2026 à 11h50')).toBeInTheDocument();
  });

  it('profil des pré-inscrits : nationalités et pyramide de l’API', async () => {
    simulerApi();
    afficher('/enrolement');

    const profil = within(await screen.findByRole('region', { name: 'Profil des pré-inscrits' }));
    const liste = within(profil.getByRole('list', { name: 'Pré-inscriptions par nationalité' }));
    expect(await liste.findByText('TOGO')).toBeInTheDocument();
    expect(liste.getByText(texte('603 120'))).toBeInTheDocument();
    expect(liste.getAllByRole('listitem').map((l) => l.firstChild?.textContent)).toEqual([
      'TOGO',
      'BENIN',
      'GHANA',
      'NIGERIA',
      'BURKINA FASO',
      'Autres',
    ]);
    const pyramide = within(
      profil.getByRole('table', { name: 'Répartition des pré-inscriptions par tranche d’âge et par sexe' }),
    );
    expect(pyramide.getByText(texte('79 000'))).toBeInTheDocument();
    const derniere = pyramide.getAllByRole('row').at(-1)!;
    expect(within(derniere).getByRole('rowheader').textContent).toBe('Âge inconnu');
    expect(within(derniere).getByText(texte('1 837'))).toBeInTheDocument();
    expect(within(derniere).getByText(texte('2 583'))).toBeInTheDocument();
  });

  it('pré-inscription : femmes et hommes, sans pourcentage ni note', async () => {
    simulerApi({ '/enrolement/preinscriptions': { ...PREINSCRIPTIONS, femmes: 300000, hommes: 200000 } });
    afficher('/enrolement');

    const pre = within(await screen.findByRole('region', { name: 'Pré-inscription' }));
    expect(await pre.findByText(texte('300 000'))).toBeInTheDocument();
    expect(pre.getByText(texte('200 000'))).toBeInTheDocument();
    expect(pre.queryByText(/sexes connus/)).not.toBeInTheDocument();
    expect(pre.queryByRole('note')).not.toBeInTheDocument();
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
