import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { nf, pct } from '../../lib/format';
import { afficher, simulerApi } from '../../test/apiSimulee';

const texte = (t: string) => t.replace(/\s+/g, ' ');
const blocAffiche = async () =>
  within(await screen.findByRole('region', { name: 'Où s’arrêtent les paquets' }));
const noms = (liste: HTMLElement) =>
  within(liste)
    .getAllByRole('listitem')
    .map((l) => l.querySelector('.motif-arret__nom')?.textContent);

describe('Où s’arrêtent les paquets', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('trois onglets avec leur nombre, Rejetés ouvert ; les paquets sans NIU en sous-titre', async () => {
    simulerApi();
    afficher('/enrolement');

    const bloc = await blocAffiche();
    // 86 496 rejetés + 9 218 échoués + 123 639 en cours, comme le bloc Devenir.
    await waitFor(() =>
      expect(bloc.getByText(/paquets n’ont pas encore abouti à un NIU/)).toHaveTextContent(
        texte(`${nf(219353)} paquets n’ont pas encore abouti à un NIU.`),
      ),
    );
    expect(bloc.getByText('Ensemble du Togo')).toBeInTheDocument();
    const onglets = within(bloc.getByRole('tablist', { name: 'Devenir des paquets sans NIU' }));
    expect(onglets.getAllByRole('tab').map((o) => texte(o.textContent ?? ''))).toEqual([
      texte(`Rejetés${nf(86496)}`),
      texte(`Échoués${nf(9218)}`),
      texte(`En cours${nf(123639)}`),
    ]);
    expect(onglets.getByRole('tab', { name: /^Rejetés/, selected: true })).toBeInTheDocument();
  });

  it('Rejetés : motif, paquets et part, étape et message de MOSIP, du plus fréquent au moins fréquent', async () => {
    simulerApi();
    afficher('/enrolement');

    const bloc = await blocAffiche();
    const liste = await bloc.findByRole('list', { name: 'Rejetés par motif' });
    // La liste existe avant la réponse (vide) : attendre les lignes de l'API.
    await within(liste).findByText('Rejeté par le superviseur du centre');
    expect(noms(liste)).toEqual([
      'Rejeté par le superviseur du centre',
      'Doublon biométrique trouvé par l’ABIS',
      'Doublon confirmé par le vérificateur',
      'Autres cas',
    ]);
    const [premiere, , troisieme, autres] = within(liste).getAllByRole('listitem');
    expect(premiere).toHaveTextContent(texte(`${nf(50133)}${pct(50133 / 86496)}`));
    expect(premiere).toHaveTextContent('Validation du paquet · Rejected by Supervisor');
    expect(within(premiere).getByText('Rejected by Supervisor')).toHaveAttribute('lang', 'en');
    // Un motif posé à plusieurs étapes : l'étape principale et le nombre des autres.
    expect(troisieme).toHaveTextContent(
      'Vérification manuelle et 6 autres étapes · Match Found by Manual Verifier',
    );
    // « Autres cas » : ce que la ligne regroupe, sans message.
    expect(autres.querySelector('.motif-arret__source')).toHaveTextContent('Motifs de moins de 1 % chacun');
    expect(autres).toHaveClass('motif-arret--autres');
    // Plus de ligne « À vérifier » (décision du 28/10/2026).
    expect(bloc.queryByText(/À vérifier/)).not.toBeInTheDocument();
  });

  it('En cours, au clic : sans activité depuis plus de 30 jours, en tête et par motif', async () => {
    simulerApi();
    afficher('/enrolement');
    const utilisateur = userEvent.setup();

    const bloc = await blocAffiche();
    await bloc.findByText('Rejeté par le superviseur du centre');
    await utilisateur.click(bloc.getByRole('tab', { name: /^En cours/ }));

    expect(bloc.getByRole('tab', { name: /^En cours/, selected: true })).toBeInTheDocument();
    expect(bloc.getByText(/sans activité depuis plus de 30 jours/)).toHaveTextContent(
      texte(`${nf(59264)} sans activité depuis plus de 30 jours`),
    );
    const liste = bloc.getByRole('list', { name: 'En cours par motif' });
    const file = within(liste).getByText('En file d’attente de vérification manuelle').closest('li')!;
    expect(file.querySelector('.motif-arret__detail')).toHaveTextContent(
      texte(`${nf(58834)} sans activité depuis 30 jours · ${nf(112618 - 58834)} récents`),
    );
    expect(bloc.queryByRole('list', { name: 'Rejetés par motif' })).not.toBeInTheDocument();
  });

  it('reste national', async () => {
    const appels = simulerApi();
    afficher('/enrolement?zone=SAV');

    await blocAffiche();
    await waitFor(() => expect(appels.some((u) => u.pathname.endsWith('/enrolement/motifs'))).toBe(true));
    const lus = appels.filter((u) => u.pathname.endsWith('/enrolement/motifs'));
    expect(lus.every((u) => !u.searchParams.has('zone'))).toBe(true);
  });

  it('sans réponse de l’API : trois onglets à 0, sans ligne ni message', async () => {
    simulerApi({ '/enrolement/motifs': undefined });
    afficher('/enrolement');

    const bloc = await blocAffiche();
    await waitFor(() => expect(bloc.queryByText('Chargement des chiffres…')).not.toBeInTheDocument());
    expect(bloc.getAllByRole('tab')).toHaveLength(3);
    expect(bloc.getAllByRole('tab').map((o) => o.querySelector('.arrets__nombre')?.textContent)).toEqual([
      '0',
      '0',
      '0',
    ]);
    expect(bloc.getByText(/paquets n’ont pas encore abouti/)).toHaveTextContent(/^0 paquets/);
    expect(
      within(bloc.getByRole('list', { name: 'Rejetés par motif' })).queryAllByRole('listitem'),
    ).toHaveLength(0);
    expect(bloc.queryByRole('alert')).not.toBeInTheDocument();
  });
});
