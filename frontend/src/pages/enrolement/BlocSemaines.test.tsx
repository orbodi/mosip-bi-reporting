import { screen, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { SEMAINES, afficher, simulerApi } from '../../test/apiSimulee';

const bloc = () => within(screen.getByRole('region', { name: 'Inscriptions et NIU par semaine' }));
const blocAffiche = async () =>
  within(await screen.findByRole('region', { name: 'Inscriptions et NIU par semaine' }));
// Testing Library ramène les espaces fines et insécables à des espaces simples avant de comparer.
const texte = (t: string) => t.replace(/\s+/g, ' ');

describe('Inscriptions et NIU par semaine', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('lit la dernière semaine complète et donne le tableau des 12 semaines', async () => {
    simulerApi();
    afficher('/enrolement');

    expect(
      await (
        await blocAffiche()
      ).findByText(texte('Semaine du 5 janvier : 20 230 inscriptions, 17 626 NIU générés (87,1 %).')),
    ).toBeInTheDocument();
    expect(bloc().getByText('12 dernières semaines complètes.')).toBeInTheDocument();
    expect(
      bloc().getByRole('img', { name: /par semaine, du 20\/10\/2025 au 05\/01\/2026/ }),
    ).toBeInTheDocument();
    const tableau = within(bloc().getByRole('table', { hidden: true }));
    expect(tableau.getAllByRole('row', { hidden: true })).toHaveLength(13);
    expect(bloc().queryByText('Ensemble du Togo')).not.toBeInTheDocument();
  });

  it('suit la période mais pas le filtre Région, et le signale', async () => {
    const appels = simulerApi();
    afficher('/enrolement?periode=30j&region=KAR');

    expect(await (await blocAffiche()).findByText('Ensemble du Togo')).toHaveAttribute(
      'title',
      'Ce bloc ne suit pas le filtre Région',
    );
    const semaines = appels.filter((u) => u.pathname.endsWith('/enrolement/semaines'));
    expect(semaines.at(-1)?.search).toBe('?du=2025-12-16&au=2026-01-14');
    expect(bloc().getByText(/12 semaines complètes jusqu’à la fin de la période/)).toBeInTheDocument();
  });

  it('n’affiche pas de NIU tant que leur source n’est pas alimentée', async () => {
    simulerApi({ '/enrolement/semaines': { ...SEMAINES, niuDisponibles: false } });
    afficher('/enrolement');

    expect(
      await (await blocAffiche()).findByText(texte('Semaine du 5 janvier : 20 230 inscriptions.')),
    ).toBeInTheDocument();
    expect(bloc().getByRole('note')).toHaveTextContent('source pas encore alimentée');
    expect(
      within(bloc().getByRole('list', { name: 'Légende' })).queryByText('NIU générés'),
    ).not.toBeInTheDocument();
  });
});
