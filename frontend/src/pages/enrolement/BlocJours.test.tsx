import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { nf } from '../../lib/format';
import { JOURS, afficher, simulerApi } from '../../test/apiSimulee';

const bloc = () => within(screen.getByRole('region', { name: 'Inscriptions et NIU par jour' }));
const blocAffiche = async () =>
  within(await screen.findByRole('region', { name: 'Inscriptions et NIU par jour' }));
// Testing Library ramène les espaces fines et insécables à des espaces simples avant de comparer.
const texte = (t: string) => t.replace(/\s+/g, ' ');

describe('Inscriptions et NIU par jour', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('par défaut : aujourd’hui et les 6 jours précédents, en graphique', async () => {
    simulerApi();
    afficher('/enrolement');

    // Du 08/01 au 14/01 (jour en cours) : 4 210 à 4 260 inscriptions, puis 2 134 aujourd'hui.
    expect(
      await (
        await blocAffiche()
      ).findByText(
        texte('Du 8 au 14 janvier : 27 544 inscriptions, 17 798 NIU générés (jusqu’à aujourd’hui)'),
      ),
    ).toBeInTheDocument();
    expect(bloc().getByRole('tab', { name: 'Graphique', selected: true })).toBeInTheDocument();
    expect(
      bloc().getByRole('img', { name: /par jour, du 08\/01\/2026 au 14\/01\/2026/ }),
    ).toBeInTheDocument();
    expect(
      within(bloc().getByRole('list', { name: 'Légende' })).getByText('NIU générés'),
    ).toBeInTheDocument();
    expect(bloc().getByRole('button', { name: 'Semaine suivante' })).toBeDisabled();
  });

  it('Tableau : un jour par ligne, aujourd’hui signalé, total de la semaine', async () => {
    simulerApi();
    afficher('/enrolement');
    const utilisateur = userEvent.setup();

    await (await blocAffiche()).findByText(/27 544 inscriptions/);
    await utilisateur.click(bloc().getByRole('tab', { name: 'Tableau' }));

    const lignes = within(bloc().getByRole('table')).getAllByRole('row');
    // En-tête, 7 jours, total.
    expect(lignes).toHaveLength(9);
    expect(lignes[1]).toHaveTextContent(texte(`jeu. 08/01${nf(4210)}${nf(2710)}`));
    expect(lignes[7]).toHaveTextContent(texte(`mer. 14/01 (aujourd’hui)${nf(2134)}${nf(1388)}`));
    expect(lignes[8]).toHaveTextContent(texte(`Total${nf(27544)}${nf(17798)}`));
  });

  it('recule d’une semaine à la fois, jusqu’à trois semaines en arrière', async () => {
    simulerApi();
    afficher('/enrolement');
    const utilisateur = userEvent.setup();

    await (await blocAffiche()).findByText(/27 544 inscriptions/);
    await utilisateur.click(bloc().getByRole('button', { name: 'Semaine précédente' }));
    expect(
      bloc().getByText(texte('Du 1er au 7 janvier : 29 190 inscriptions, 18 690 NIU générés')),
    ).toBeInTheDocument();
    expect(bloc().getByRole('button', { name: 'Semaine suivante' })).toBeEnabled();

    await utilisateur.click(bloc().getByRole('button', { name: 'Semaine précédente' }));
    await utilisateur.click(bloc().getByRole('button', { name: 'Semaine précédente' }));
    expect(bloc().getByText(/^Du 18 au 24 décembre : /)).toBeInTheDocument();
    expect(bloc().getByRole('button', { name: 'Semaine précédente' })).toBeDisabled();

    await utilisateur.click(bloc().getByRole('button', { name: 'Semaine suivante' }));
    expect(bloc().getByText(/^Du 25 au 31 décembre : /)).toBeInTheDocument();
  });

  it('affiche 0 NIU, sans message, tant que leur source n’est pas alimentée', async () => {
    simulerApi({ '/enrolement/jours': { ...JOURS, niuDisponibles: false } });
    afficher('/enrolement');

    expect(
      await (
        await blocAffiche()
      ).findByText(texte('Du 8 au 14 janvier : 27 544 inscriptions, 0 NIU générés (jusqu’à aujourd’hui)')),
    ).toBeInTheDocument();
    expect(bloc().queryByRole('note')).not.toBeInTheDocument();
  });

  it('lit l’API sans période ni zone : il suit la date du jour', async () => {
    const appels = simulerApi();
    afficher('/enrolement?periode=30j&region=KAR');

    await blocAffiche();
    await waitFor(() => expect(appels.some((u) => u.pathname.endsWith('/enrolement/jours'))).toBe(true));
    expect(appels.filter((u) => u.pathname.endsWith('/enrolement/jours')).every((u) => u.search === '')).toBe(
      true,
    );
  });

  it('sans réponse de l’API : les 7 jours à 0, sans message', async () => {
    simulerApi({ '/enrolement/jours': undefined });
    afficher('/enrolement');
    const utilisateur = userEvent.setup();

    const b = await blocAffiche();
    await waitFor(() => expect(b.queryByText('Chargement des chiffres…')).not.toBeInTheDocument());
    expect(b.getByText(/: 0 inscriptions, 0 NIU générés/)).toBeInTheDocument();
    await utilisateur.click(b.getByRole('tab', { name: 'Tableau' }));
    const lignes = within(b.getByRole('table')).getAllByRole('row');
    expect(lignes).toHaveLength(9);
    expect(
      lignes.slice(1).every((l) => [...l.querySelectorAll('td')].every((c) => c.textContent === '0')),
    ).toBe(true);
    expect(b.queryByRole('alert')).not.toBeInTheDocument();
  });
});
