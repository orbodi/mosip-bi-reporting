import { screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { nf, pct } from '../../lib/format';
import { afficher, simulerApi } from '../../test/apiSimulee';

const texte = (t: string) => t.replace(/\s+/g, ' ');
const blocAffiche = async () =>
  within(await screen.findByRole('region', { name: 'Où s’arrêtent les paquets' }));

describe('Où s’arrêtent les paquets', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('compte les paquets sans NIU et les répartit en rejetés, échoués et en cours', async () => {
    simulerApi();
    afficher('/enrolement');

    const bloc = await blocAffiche();
    // 86 496 rejetés + 9 218 échoués + 123 639 en cours, comme le bloc Devenir.
    await waitFor(() =>
      expect(bloc.getByText(/paquets n’ont pas de NIU/)).toHaveTextContent(
        texte(`${nf(219353)} paquets n’ont pas de NIU`),
      ),
    );
    expect(bloc.getByText('Ensemble du Togo')).toBeInTheDocument();
    expect(bloc.getAllByRole('heading', { level: 3 }).map((h) => h.textContent)).toEqual([
      'Rejetés',
      'Échoués',
      'En cours',
    ]);
    const rejets = within(bloc.getByRole('article', { name: 'Rejetés' }));
    expect(rejets.getByText(texte(nf(86496)))).toBeInTheDocument();
    expect(
      rejets.getByText(texte(`paquets, ${pct(86496 / 219353)} des paquets sans NIU`)),
    ).toBeInTheDocument();
  });

  it('donne pour chaque ligne le motif, l’étape et le message de MOSIP, du plus fréquent au moins fréquent', async () => {
    simulerApi();
    afficher('/enrolement');

    const bloc = await blocAffiche();
    const rejets = within(await bloc.findByRole('list', { name: 'Rejetés par motif' }));
    // La liste existe avant la réponse (vide) : attendre les lignes de l'API.
    await rejets.findByText('Rejeté par le superviseur du centre');
    expect(rejets.getAllByRole('listitem').map((l) => l.firstChild?.firstChild?.textContent)).toEqual([
      'Rejeté par le superviseur du centre',
      'Doublon biométrique trouvé par l’ABIS',
      'Doublon confirmé par le vérificateur',
      'Autres cas',
    ]);
    const premiere = rejets.getAllByRole('listitem')[0];
    expect(premiere).toHaveTextContent(texte(nf(50133)));
    expect(premiere).toHaveTextContent('Validation du paquet · Rejected by Supervisor');
    expect(within(premiere).getByText('Rejected by Supervisor')).toHaveAttribute('lang', 'en');
    expect(premiere).toHaveTextContent(texte(pct(50133 / 86496)));
    expect(premiere).toHaveClass('etape-arret--principale');
    // Ce qu'il faut vérifier, sous le motif.
    expect(premiere).toHaveTextContent(
      'À vérifier : Le superviseur a refusé le paquet au poste ; MOSIP ne transmet pas sa raison.',
    );
    // « Autres cas » : ni étape, ni message, ni piste.
    const autres = rejets.getAllByRole('listitem')[3];
    expect(autres.querySelector('.etape-arret__source')).toBeEmptyDOMElement();
    expect(within(autres).queryByText(/À vérifier/)).not.toBeInTheDocument();
  });

  it('en cours : bloqués depuis plus de 30 jours, en tête de colonne et par motif', async () => {
    simulerApi();
    afficher('/enrolement');

    const bloc = await blocAffiche();
    const enCours = within(await bloc.findByRole('article', { name: 'En cours' }));
    // La ligne des bloqués est là avant la réponse, avec 0 : attendre le chiffre de l'API.
    await waitFor(() =>
      expect(enCours.getByText(/bloqués depuis plus de 30 jours/)).toHaveTextContent(
        texte(`${nf(59264)} bloqués depuis plus de 30 jours`),
      ),
    );
    const file = enCours.getByText('En file d’attente de vérification manuelle').closest('li')!;
    expect(within(file).getByText(/récents/)).toHaveTextContent(
      texte(`${nf(58834)} bloqués · ${nf(112618 - 58834)} récents`),
    );
    expect(enCours.getByRole('list', { name: 'Légende' })).toHaveTextContent(
      'Bloqués : aucune activité depuis plus de 30 jours',
    );
  });

  it('reste national', async () => {
    const appels = simulerApi();
    afficher('/enrolement?zone=SAV');

    await blocAffiche();
    await waitFor(() => expect(appels.some((u) => u.pathname.endsWith('/enrolement/motifs'))).toBe(true));
    const lus = appels.filter((u) => u.pathname.endsWith('/enrolement/motifs'));
    expect(lus.every((u) => !u.searchParams.has('zone'))).toBe(true);
  });

  it('sans réponse de l’API : trois colonnes à 0, sans ligne ni message', async () => {
    simulerApi({ '/enrolement/motifs': undefined });
    afficher('/enrolement');

    const bloc = await blocAffiche();
    await waitFor(() => expect(bloc.queryByText('Chargement des chiffres…')).not.toBeInTheDocument());
    expect(bloc.getAllByRole('article')).toHaveLength(3);
    expect(bloc.getByText(/paquets n’ont pas de NIU/)).toHaveTextContent(/^0 paquets/);
    expect(bloc.getAllByText('0').length).toBeGreaterThanOrEqual(4);
    expect(bloc.queryByRole('alert')).not.toBeInTheDocument();
    expect(bloc.queryAllByRole('listitem').filter((l) => l.closest('.arret__etapes'))).toHaveLength(0);
  });
});
