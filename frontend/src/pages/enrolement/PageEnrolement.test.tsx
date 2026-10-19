import { screen, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { afficher, simulerApi } from '../../test/apiSimulee';

describe('Page Enrôlement', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('présente les blocs dans l’ordre de la maquette ; seule la pré-inscription reste à construire', async () => {
    simulerApi();
    afficher('/enrolement');

    await screen.findByRole('heading', { name: 'Territoire : vue nationale' });
    expect(screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent)).toEqual([
      'Devenir des inscriptions',
      'Inscriptions et NIU par semaine',
      'Territoire : vue nationale',
      'NIU générés par âge et par sexe',
      'Top des centres',
      'Blocs à construire',
    ]);
    const aConstruire = within(screen.getByRole('region', { name: 'Blocs à construire' }));
    expect(aConstruire.getAllByRole('listitem').map((l) => l.textContent)).toEqual(['Pré-inscription']);
  });

  it('âge et sexe : « non disponible », jamais de chiffres estimés', async () => {
    simulerApi();
    afficher('/enrolement?region=SAV');

    const bloc = within(await screen.findByRole('region', { name: 'NIU générés par âge et par sexe' }));
    expect(bloc.getByRole('note')).toHaveTextContent('Non disponible');
    expect(await bloc.findByText(/Région Savanes/)).toBeInTheDocument();
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
