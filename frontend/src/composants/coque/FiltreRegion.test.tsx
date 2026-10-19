import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { afficher, simulerApi } from '../../test/apiSimulee';

describe('Filtre Région', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('propose toutes les régions du nord au sud et garde le choix dans l’adresse', async () => {
    simulerApi();
    const routeur = afficher('/enrolement?periode=7j');
    const utilisateur = userEvent.setup();

    const bouton = await screen.findByRole('button', { name: /Région/ });
    expect(bouton).toHaveTextContent('Toutes les régions');
    await utilisateur.click(bouton);
    const options = within(await screen.findByRole('listbox')).getAllByRole('option');
    expect(options.map((o) => o.textContent)).toEqual([
      'Toutes les régions',
      'Savanes',
      'Kara',
      'Centrale',
      'Plateaux',
      'Maritime',
      'Grand Lomé',
    ]);
    await utilisateur.click(screen.getByRole('option', { name: 'Kara' }));

    expect(routeur.state.location.search).toEqual({ periode: '7j', region: 'KAR' });
    expect(await screen.findByRole('button', { name: /Région/ })).toHaveTextContent('Kara');
  });

  it('n’offre que sa région à un utilisateur régional', async () => {
    simulerApi({ '/meta/regions': [{ code: 'KAR', nom: 'Kara' }] });
    afficher('/enrolement');

    const bouton = await screen.findByRole('button', { name: /Région/ });
    await vi.waitFor(() => expect(bouton).toHaveTextContent('Kara'));
    expect(bouton).toBeDisabled();
  });

  it('ignore un code de région inconnu une fois la liste chargée', async () => {
    simulerApi();
    afficher('/enrolement?region=XYZ');

    expect(await screen.findByRole('heading', { name: 'Territoire : vue nationale' })).toBeInTheDocument();
  });
});
