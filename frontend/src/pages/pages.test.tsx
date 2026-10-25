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
    ['/impression-cartes', 'Impression et remise'],
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

  it('Vue d’ensemble : étapes d’enrôlement de l’API, autres étapes à 0', async () => {
    simulerApi();
    afficher('/');

    const parcours = within(
      await screen.findByRole('region', { name: 'De la pré-inscription à la carte en main' }),
    );
    expect(await parcours.findByText('3 278 239'.replace(/\s/g, ' '))).toBeInTheDocument();
    expect(parcours.getByText('Pré-inscriptions')).toBeInTheDocument();
    const regions = within(screen.getByRole('region', { name: 'Le parcours par région' }));
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
