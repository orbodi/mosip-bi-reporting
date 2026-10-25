import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { afficher, simulerApi } from '../../test/apiSimulee';

const bloc = () => within(screen.getByRole('region', { name: 'Top des centres' }));
const blocAffiche = async () => within(await screen.findByRole('region', { name: 'Top des centres' }));

describe('Top des centres', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('classe d’abord par inscriptions, avec la préfecture et la région de chaque centre', async () => {
    simulerApi();
    afficher('/enrolement');

    expect(await (await blocAffiche()).findByText('EPP Doumassesse I G/B')).toBeInTheDocument();
    expect(bloc().getByRole('tab', { name: 'Plus d’enregistrements', selected: true })).toBeInTheDocument();
    expect(bloc().getAllByText('Golfe, Grand Lomé')).toHaveLength(2);
    expect(bloc().getByRole('columnheader', { name: 'Inscriptions' })).toBeInTheDocument();
  });

  it('change de classement avec les onglets et le demande à l’API', async () => {
    const appels = simulerApi();
    afficher('/enrolement');
    const utilisateur = userEvent.setup();

    await (await blocAffiche()).findByText('EPP Doumassesse I G/B');
    await utilisateur.click(bloc().getByRole('tab', { name: 'Plus d’échecs' }));
    expect(await (await blocAffiche()).findByText('EPP Worgou G/A')).toBeInTheDocument();
    expect(bloc().getByRole('columnheader', { name: 'Échecs' })).toBeInTheDocument();
    expect(appels.some((u) => u.searchParams.get('classement') === 'echecs')).toBe(true);

    await utilisateur.click(bloc().getByRole('tab', { name: 'Plus de rejets' }));
    expect(
      await (await blocAffiche()).findByText('Aucun centre de ce classement sur la période.'),
    ).toBeInTheDocument();
  });

  it('reste national quand une région est ouverte dans le bloc Territoire', async () => {
    const appels = simulerApi();
    afficher('/enrolement?region=GLO');

    await (await blocAffiche()).findByText('EPP Doumassesse I G/B');
    expect(bloc().queryByText('Région Grand Lomé')).not.toBeInTheDocument();
    const centres = appels.filter((u) => u.pathname.endsWith('/enrolement/centres'));
    expect(centres.every((u) => !u.searchParams.has('zone'))).toBe(true);
  });

  it('sans réponse de l’API, garde les cinq rangs du classement', async () => {
    simulerApi({ '/enrolement/centres': undefined });
    afficher('/enrolement');

    const b = await blocAffiche();
    expect(b.getAllByRole('row')).toHaveLength(6);
    expect(b.queryByRole('alert')).not.toBeInTheDocument();
    expect(b.getAllByText('0')).toHaveLength(5);
  });
});
