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

  it('nomme chaque étape en français, le code MOSIP en complément, dans l’ordre du traitement', async () => {
    simulerApi();
    afficher('/enrolement');

    const bloc = await blocAffiche();
    const rejets = within(await bloc.findByRole('list', { name: 'Rejetés par étape' }));
    // La liste existe avant la réponse (vide) : attendre les étapes de l'API.
    await rejets.findByText('Refus au poste');
    expect(rejets.getAllByRole('listitem').map((l) => l.firstChild?.firstChild?.textContent)).toEqual([
      'Refus au poste',
      'Déduplication démographique',
      'Déduplication biométrique',
      'Autres étapes',
    ]);
    expect(rejets.getByText('BIOGRAPHIC_VERIFICATION')).toBeInTheDocument();
    // REFUS_POSTE est un code du BI, pas de MOSIP : seul le libellé est montré.
    expect(bloc.queryByText('REFUS_POSTE')).not.toBeInTheDocument();
    expect(rejets.getByText(texte(pct(50133 / 86496)))).toBeInTheDocument();
  });

  it('en cours : bloqués depuis plus de 30 jours, en tête de colonne et par étape', async () => {
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
    const manuelle = enCours.getByText('Vérification manuelle').closest('li')!;
    expect(within(manuelle).getByText(/récents/)).toHaveTextContent(
      texte(`${nf(58834)} bloqués · ${nf(112618 - 58834)} récents`),
    );
    expect(enCours.getByRole('list', { name: 'Légende' })).toHaveTextContent(
      'Bloqués : aucune activité depuis plus de 30 jours',
    );
  });

  it('reste national et sans période (stock des en cours)', async () => {
    const appels = simulerApi();
    afficher('/enrolement?zone=SAV');

    await blocAffiche();
    await waitFor(() => expect(appels.some((u) => u.pathname.endsWith('/enrolement/en-cours'))).toBe(true));
    const lus = appels.filter((u) => /\/enrolement\/(etapes|en-cours)$/.test(u.pathname));
    expect(lus.every((u) => !u.searchParams.has('zone'))).toBe(true);
    expect(lus.filter((u) => u.pathname.endsWith('en-cours')).every((u) => !u.searchParams.has('du'))).toBe(
      true,
    );
  });

  it('sans réponse de l’API : trois colonnes à 0, sans étape ni message', async () => {
    simulerApi({ '/enrolement/etapes': undefined, '/enrolement/en-cours': undefined });
    afficher('/enrolement');

    const bloc = await blocAffiche();
    await waitFor(() => expect(bloc.queryByText('Chargement des chiffres…')).not.toBeInTheDocument());
    expect(bloc.getAllByRole('article')).toHaveLength(3);
    expect(bloc.getByText(/paquets n’ont pas de NIU/)).toHaveTextContent(/^0 paquets/);
    expect(bloc.getAllByText('0').length).toBeGreaterThanOrEqual(4);
    expect(bloc.queryByRole('alert')).not.toBeInTheDocument();
    expect(bloc.queryByText('Vérification manuelle')).not.toBeInTheDocument();
  });
});
