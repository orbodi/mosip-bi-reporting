import { screen, waitFor, within } from '@testing-library/react';
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
    ['/authentifications', 'Requêtes d’authentification'],
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
