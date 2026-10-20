import { screen, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { afficher, simulerApi } from '../../test/apiSimulee';

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
    // Pré-inscription : source en attente (décision P1), mise en page et chiffres « – ».
    const pre = within(screen.getByRole('region', { name: 'Pré-inscription' }));
    expect(pre.getByRole('note')).toHaveTextContent('pas encore raccordée');
    expect(pre.getByText('Non mesuré : rendez-vous et inscriptions non reliés')).toBeInTheDocument();
  });

  it('âge et sexe : « non disponible », jamais de chiffres estimés', async () => {
    simulerApi();
    afficher('/enrolement?region=SAV');

    const bloc = within(await screen.findByRole('region', { name: 'NIU générés par âge et par sexe' }));
    expect(bloc.getByRole('note')).toHaveTextContent('Non disponible');
    expect(await bloc.findByText(/Région Savanes/)).toBeInTheDocument();
    // Pyramide de la maquette : 8 tranches, femmes et hommes à « – », jamais 0.
    const pyramide = within(
      bloc.getByRole('table', { name: 'Répartition des NIU par tranche d’âge et par sexe' }),
    );
    expect(pyramide.getAllByRole('rowheader').map((t) => t.textContent)).toEqual([
      '60 ans et +',
      '46 à 60',
      '36 à 45',
      '26 à 35',
      '19 à 25',
      '15 à 18',
      '6 à 14',
      '0 à 5',
    ]);
    expect(pyramide.getAllByRole('cell').every((c) => c.textContent === '–')).toBe(true);
    expect(bloc.getByText(/^Femmes :/)).toHaveTextContent('Femmes : –');
    expect(bloc.getByText(/^Hommes :/)).toHaveTextContent('Hommes : –');
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
