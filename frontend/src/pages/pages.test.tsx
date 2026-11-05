import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { afficher, simulerApi } from '../test/apiSimulee';

/** Bouton d'une liste de l'Exploration, retrouvé par son libellé (« Préfecture », « Commune »…). */
const boutonChoix = (libelle: string) => {
  const etiquette = screen
    .getAllByText(libelle, { selector: '.champ-choix__libelle' })
    .find((e) => e.closest('.champ-choix'));
  const bouton = etiquette?.closest('.champ-choix')?.querySelector('button');
  if (!bouton) throw new Error(`Liste « ${libelle} » introuvable`);
  return bouton;
};

describe('Pages de la maquette', () => {
  afterEach(() => vi.unstubAllGlobals());

  it.each([
    ['/abis', 'Transactions ABIS'],
    ['/idps', 'Ordres d’impression'],
  ])('%s : mise en page de la maquette, indicateurs à 0, sans note de source', async (chemin, bloc) => {
    simulerApi();
    afficher(chemin);

    const premier = within(await screen.findByRole('region', { name: bloc }));
    expect(premier.getAllByText('0').length).toBeGreaterThanOrEqual(2);
    expect(premier.queryByText('–')).not.toBeInTheDocument();
    expect(screen.queryByText(/pas encore raccordée|non disponible|indisponible/i)).not.toBeInTheDocument();
  });

  it('Impression des cartes : chiffres de l’API, annulées parmi les demandes, attente et centres', async () => {
    simulerApi();
    afficher('/impression-cartes');

    const bloc = within(await screen.findByRole('region', { name: 'Impression et remise' }));
    expect(await bloc.findByText(/^4\s643\s568$/)).toBeInTheDocument();
    expect(bloc.getByText(/76,0\s% des 6\s107\s359 cartes expédiées/)).toBeInTheDocument();
    expect(bloc.getByText(/hors ligne · 197\s370 en ligne · 32 par le support/)).toBeInTheDocument();
    const demandes = within(bloc.getByRole('group', { name: 'Demandes' }));
    expect(demandes.getByText(/^693$/)).toBeInTheDocument();
    expect(
      await demandes.findByText('Parmi les demandes : photo 643, sexe 36, nom 10, personnalisation 4'),
    ).toBeInTheDocument();
    expect(demandes.getByText('Dernière reçue le 07/01/2026')).toBeInTheDocument();
    expect(demandes.getByText(/^172\s354$/)).toBeInTheDocument();
    expect(demandes.getByText('Parmi les demandes ; dernière reçue le 09/01/2026')).toBeInTheDocument();
    expect(within(bloc.getByRole('group', { name: 'Cartes' })).getByText(/^31 jours$/)).toBeInTheDocument();

    const rejets = within(screen.getByRole('region', { name: 'Rejetées et annulées par semaine' }));
    expect(
      await rejets.findByText('Sur ces 12 semaines : 1 demande rejetée, 12 annulées.'),
    ).toBeInTheDocument();
    const attente = within(screen.getByRole('region', { name: 'Depuis quand ces cartes attendent' }));
    expect(await attente.findByText(/83,3\s% des cartes à remettre/)).toBeInTheDocument();
    const centres = within(screen.getByRole('region', { name: 'Top des centres' }));
    expect(await centres.findByText('EPP Doumassesse')).toBeInTheDocument();
  });

  it('Impression des cartes : régions, alerte au-delà de la moitié, puis préfectures de la région choisie', async () => {
    const appels = simulerApi();
    afficher('/impression-cartes');
    const utilisateur = userEvent.setup();

    const geo = within(await screen.findByRole('region', { name: 'Cartes à remettre par région' }));
    // La ligne avec ses chiffres (et non celle, sans chiffres, affichée avant la réponse de l'API).
    const savanes = await geo.findByRole('row', { name: /Savanes.*55,4/ });
    expect(within(savanes).getByRole('img', { name: /plus de la moitié/ })).toBeInTheDocument();
    expect(within(savanes).getByText(/55,4\s%/)).toBeInTheDocument();
    await utilisateur.click(within(savanes).getByRole('button', { name: /Savanes/ }));
    expect(await screen.findByRole('rowheader', { name: 'Tône' })).toBeInTheDocument();
    expect(
      appels.some((u) => u.pathname.endsWith('/cartes/territoire') && u.searchParams.get('zone') === 'SAV'),
    ).toBe(true);
  });

  it('Impression des cartes : sans réponse de l’API, mise en page gardée et chiffres à 0', async () => {
    simulerApi({
      '/cartes/impression': undefined,
      '/cartes/annulations': undefined,
      '/cartes/semaines': undefined,
      '/cartes/territoire': undefined,
      '/cartes/attente': undefined,
      '/cartes/centres': undefined,
    });
    afficher('/impression-cartes');

    const bloc = within(await screen.findByRole('region', { name: 'Impression et remise' }));
    expect(bloc.getAllByText('0').length).toBeGreaterThanOrEqual(2);
    // Annulées et erreurs d'envoi à l'IDPS, sans motif ni date tant que l'API ne répond pas.
    expect(bloc.getAllByText('Parmi les demandes')).toHaveLength(2);
    expect(screen.queryByText(/pas encore raccordée|non disponible|indisponible/i)).not.toBeInTheDocument();
  });

  it('Authentifications : usagers, types, causes, partenaires et paquets depuis l’API, jamais additionnés', async () => {
    simulerApi();
    afficher('/authentifications');

    const usagers = within(
      await screen.findByRole('region', { name: 'Requêtes d’authentification des usagers' }),
    );
    expect(await usagers.findByText(/^2\s186$/)).toBeInTheDocument();
    expect(usagers.getByText(/^Atos, 75,3\s% des requêtes$/)).toBeInTheDocument();
    expect(usagers.getByText(/2\s380 codes envoyés, 60,5\s% utilisés$/)).toBeInTheDocument();

    const types = within(screen.getByRole('region', { name: 'Par type d’authentification' }));
    const lignes = await types.findAllByRole('row');
    expect(lignes[1]).toHaveTextContent(/^Code OTP/);
    expect(types.getAllByRole('img', { name: 'Alerte : taux d’échec de 50 % ou plus' })).toHaveLength(2);

    const causes = within(screen.getByRole('region', { name: 'Causes des échecs' }));
    expect(await causes.findByText('Aucun mode d’authentification demandé')).toBeInTheDocument();

    const partenaires = within(screen.getByRole('region', { name: 'Partenaires et canaux' }));
    expect(await partenaires.findByRole('row', { name: /Atos Partenaire 1\s645/ })).toBeInTheDocument();
    expect(partenaires.getByText('1 partenaire raccordé')).toBeInTheDocument();
    // Le code MOSIP de l'appelant n'est jamais affiché (décision du 04/11/2026).
    expect(screen.queryByText(/AU-ANID|mosip-resident-client/)).not.toBeInTheDocument();

    const paquets = within(
      screen.getByRole('region', { name: 'Vérifications biométriques du traitement des paquets' }),
    );
    expect(await paquets.findByText(/^170\s151$/)).toBeInTheDocument();
    expect(paquets.getByText('NIU absent de la base d’authentification')).toBeInTheDocument();
    expect(paquets.getByText('Ensemble du Togo')).toBeInTheDocument();
  });

  it('Authentifications : sans réponse de l’API, mise en page gardée et chiffres à 0', async () => {
    simulerApi({
      '/authentifications/usagers': undefined,
      '/authentifications/types': undefined,
      '/authentifications/causes': undefined,
      '/authentifications/partenaires': undefined,
      '/authentifications/semaines': undefined,
      '/authentifications/paquets': undefined,
    });
    afficher('/authentifications');

    const usagers = within(
      await screen.findByRole('region', { name: 'Requêtes d’authentification des usagers' }),
    );
    expect(usagers.getAllByText('0').length).toBeGreaterThanOrEqual(2);
    const paquets = within(
      screen.getByRole('region', { name: 'Vérifications biométriques du traitement des paquets' }),
    );
    expect(paquets.getByText('Biométrie non concordante')).toBeInTheDocument();
    expect(screen.getByText('0 partenaire raccordé')).toBeInTheDocument();
    expect(screen.queryByText(/pas encore raccordée|non disponible|indisponible/i)).not.toBeInTheDocument();
  });

  it('Vue d’ensemble : étapes d’enrôlement et des cartes de l’API, part des inscrits avec carte', async () => {
    simulerApi();
    afficher('/');

    const parcours = within(
      await screen.findByRole('region', { name: 'De la pré-inscription à la carte en main' }),
    );
    expect(await parcours.findByText(/^3\s278\s239$/)).toBeInTheDocument();
    expect(parcours.getByText('Pré-inscriptions')).toBeInTheDocument();
    expect(await parcours.findByText(/^6\s195\s305$/)).toBeInTheDocument();
    expect(parcours.getByText(/^6\s107\s359$/)).toBeInTheDocument();
    expect(parcours.getAllByText(/^4\s643\s568$/).length).toBeGreaterThanOrEqual(1);
    expect(
      parcours.getByText('3 NIU de première inscription sans demande d’impression depuis plus de 7 jours.'),
    ).toBeInTheDocument();
    const regions = within(screen.getByRole('region', { name: 'Le parcours par région' }));
    const savanes = await regions.findByRole('row', { name: /Savanes.*41,9/ });
    // Savanes : 188 796 cartes remises pour 450 239 inscriptions, moins de la moitié (en gras).
    expect(await within(savanes).findByText(/^41,9\s%$/, { selector: 'strong' })).toBeInTheDocument();
    expect(await regions.findByRole('rowheader', { name: 'Grand Lomé' })).toBeInTheDocument();
  });

  it('Exploration : inscriptions par région depuis l’API, puis par préfecture de la région choisie', async () => {
    const appels = simulerApi();
    afficher('/exploration');
    const utilisateur = userEvent.setup();

    const resultat = within(await screen.findByRole('region', { name: 'Inscriptions par région' }));
    await utilisateur.click(await resultat.findByRole('button', { name: /Savanes/ }));
    expect(
      await screen.findByRole('heading', { level: 2, name: 'Inscriptions par préfecture' }),
    ).toBeInTheDocument();
    expect(
      appels.some((u) => u.pathname.endsWith('/territoire') && u.searchParams.get('zone') === 'SAV'),
    ).toBe(true);
    expect(await screen.findByRole('rowheader', { name: 'Tône' })).toBeInTheDocument();
  });

  it('Exploration : période personnalisée, un jour précis ou un intervalle, erreur si la fin précède le début', async () => {
    const appels = simulerApi();
    afficher('/exploration');
    const utilisateur = userEvent.setup();

    await screen.findByRole('region', { name: 'Inscriptions par région' });
    await utilisateur.click(boutonChoix('Période'));
    await utilisateur.click(await screen.findByRole('option', { name: 'Personnalisée' }));
    expect(screen.getByText(/laissez « Au » vide pour un seul jour/)).toBeInTheDocument();

    // Un jour précis : seulement « Du ».
    fireEvent.change(screen.getByLabelText('Du'), { target: { value: '2026-01-02' } });
    await waitFor(() =>
      expect(
        appels.some(
          (u) =>
            u.pathname.endsWith('/territoire') &&
            u.searchParams.get('du') === '2026-01-02' &&
            u.searchParams.get('au') === '2026-01-02',
        ),
      ).toBe(true),
    );
    expect(screen.getByText(/· le 02\/01\/2026 ·/)).toBeInTheDocument();

    // Un intervalle, puis une fin avant le début : message, pas de nouvel appel.
    fireEvent.change(screen.getByLabelText('Au'), { target: { value: '2026-01-10' } });
    await waitFor(() =>
      expect(appels.some((u) => u.searchParams.get('du') === '2026-01-02' && u.searchParams.get('au') === '2026-01-10')).toBe(true),
    );
    expect(screen.getByText(/· du 02\/01\/2026 au 10\/01\/2026 ·/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Du'), { target: { value: '2026-01-12' } });
    expect(await screen.findByRole('alert')).toHaveTextContent('La date de fin doit suivre la date de début.');
    expect(appels.some((u) => u.searchParams.get('du') === '2026-01-12')).toBe(false);
  });

  it('Exploration : authentifications depuis l’API, usagers ou traitement des paquets, filtres lus dans les données', async () => {
    const appels = simulerApi();
    afficher('/exploration');
    const utilisateur = userEvent.setup();

    await utilisateur.click(await screen.findByRole('tab', { name: /Authentifications/ }));
    expect(await screen.findByText(/^2\s186$/)).toBeInTheDocument();

    // Ventilation par partenaire : noms lus dans les données, sans code MOSIP.
    await utilisateur.click(boutonChoix('Afficher par'));
    await utilisateur.click(await screen.findByRole('option', { name: 'Partenaire' }));
    expect(await screen.findByRole('rowheader', { name: 'Atos' })).toBeInTheDocument();
    expect(
      appels.some((u) => u.pathname.endsWith('/exploration') && u.searchParams.get('par') === 'appelant'),
    ).toBe(true);

    // Le filtre Partenaire se remplit depuis les données.
    await utilisateur.click(boutonChoix('Partenaire'));
    expect(await screen.findByRole('option', { name: 'Portail du résident' })).toBeInTheDocument();
    await utilisateur.keyboard('{Escape}');

    // Traitement des paquets : jamais additionné aux usagers.
    await utilisateur.click(boutonChoix('Périmètre'));
    await utilisateur.click(await screen.findByRole('option', { name: 'Traitement des paquets' }));
    expect(await screen.findByRole('rowheader', { name: 'Traitement des paquets' })).toBeInTheDocument();
    expect((await screen.findAllByText(/^170\s151$/)).length).toBeGreaterThanOrEqual(1);
  });

  it('Exploration : descend jusqu’aux communes, listes en cascade et pré-inscriptions', async () => {
    const appels = simulerApi();
    afficher('/exploration');
    const utilisateur = userEvent.setup();

    // Sans région choisie, seule la liste des régions est ouverte.
    await waitFor(() => expect(boutonChoix('Préfecture')).toBeDisabled());

    let resultat = within(await screen.findByRole('region', { name: 'Inscriptions par région' }));
    await utilisateur.click(await resultat.findByRole('button', { name: /Savanes/ }));
    resultat = within(await screen.findByRole('region', { name: 'Inscriptions par préfecture' }));
    await utilisateur.click(await resultat.findByRole('button', { name: /Tône/ }));

    resultat = within(await screen.findByRole('region', { name: 'Inscriptions par commune' }));
    expect(await resultat.findByRole('rowheader', { name: 'Tône 2' })).toBeInTheDocument();
    expect(
      appels.some((u) => u.pathname.endsWith('/territoire') && u.searchParams.get('zone') === 'SAV-02'),
    ).toBe(true);
    // Fil d'Ariane du résultat : Togo › Savanes › Tône.
    expect(resultat.getByRole('button', { name: 'Togo' })).toBeInTheDocument();
    expect(resultat.getByRole('button', { name: 'Savanes' })).toBeInTheDocument();
    // Listes : préfecture et commune ouvertes (Tône choisie), canton fermé tant qu'aucune commune n'est choisie.
    await waitFor(() => expect(boutonChoix('Préfecture')).toBeEnabled());
    await waitFor(() => expect(boutonChoix('Commune')).toBeEnabled());
    expect(boutonChoix('Canton')).toBeDisabled();

    // Pré-inscriptions : nouvel indicateur de l'Enrôlement, situé à la préfecture de résidence.
    // La liste des indicateurs est dans un <details> : on l'ouvre comme le ferait un clic sur son résumé.
    document.querySelector('details.xp-indicateurs')?.setAttribute('open', '');
    const liste = within(screen.getByRole('group', { name: 'Indicateurs' }));
    await utilisateur.click(liste.getByRole('checkbox', { name: 'Pré-inscriptions' }));
    expect(await screen.findByRole('columnheader', { name: 'Pré-inscriptions' })).toBeInTheDocument();
    expect(screen.getByText(/ne sont situées qu’à la préfecture de résidence/)).toBeInTheDocument();

    await utilisateur.click(resultat.getByRole('button', { name: 'Savanes' }));
    expect(await screen.findByRole('rowheader', { name: 'Cinkassé' })).toBeInTheDocument();
  });
});
