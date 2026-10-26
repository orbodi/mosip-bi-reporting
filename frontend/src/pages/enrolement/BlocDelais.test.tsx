import { screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { nf, pct } from '../../lib/format';
import { afficher, DELAIS, simulerApi } from '../../test/apiSimulee';

const texte = (t: string) => t.replace(/\s+/g, ' ');
const blocAffiche = async () => within(await screen.findByRole('region', { name: 'Délais de traitement' }));
const carte = (nom: string) => screen.getByText(nom).closest('.indicateur') as HTMLElement;

describe('Délais de traitement', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('réception → NIU : délai médian en heures, 9 sur 10 sous la borne haute de la classe du 90e centile', async () => {
    simulerApi();
    afficher('/enrolement');

    const bloc = await blocAffiche();
    await waitFor(() =>
      expect(carte('De la réception au NIU')).toHaveTextContent(
        // Classe du 90e centile [240 h, 264 h) : 9 sur 10 en moins de 264 h.
        texte('De la réception au NIU8hdélai médian ; 9 sur 10 en moins de 264 h'),
      ),
    );
    expect(bloc.getByText('Ensemble du Togo')).toBeInTheDocument();
  });

  it('enrôlement → réception : paquets reçus en moins de 24 h, puis leur part', async () => {
    simulerApi();
    afficher('/enrolement');

    await blocAffiche();
    await waitFor(() =>
      expect(carte('De l’enrôlement à la réception')).toHaveTextContent(
        texte(
          `${nf(3009423)}paquets reçus en moins de 24 h, soit ${pct(3009423 / 3278239)} des paquets reçus`,
        ),
      ),
    );
  });

  it('synchronisés, pas encore reçus : dont plus de 7 jours', async () => {
    simulerApi();
    afficher('/enrolement');

    await blocAffiche();
    await waitFor(() =>
      expect(carte('Synchronisés, pas encore reçus')).toHaveTextContent(
        texte(`${nf(932)}paquets, dont ${nf(505)} depuis plus de 7 jours`),
      ),
    );
  });

  it('sans délai mesuré ni réponse : cartes en place, chiffres à 0', async () => {
    simulerApi({
      '/enrolement/delais': {
        ...DELAIS,
        receptionNiu: { paquets: 0, medianeH: null, centile90H: null, moins24h: 0 },
      },
      '/enrolement/synchronisation': undefined,
    });
    afficher('/enrolement');

    const bloc = await blocAffiche();
    await waitFor(() =>
      expect(carte('De la réception au NIU')).toHaveTextContent(
        texte('De la réception au NIU0hdélai médian ; 9 sur 10 en moins de 0 h'),
      ),
    );
    expect(carte('Synchronisés, pas encore reçus')).toHaveTextContent(
      'Synchronisés, pas encore reçus0paquets, dont 0 depuis plus de 7 jours',
    );
    expect(bloc.queryByRole('alert')).not.toBeInTheDocument();
  });
});
