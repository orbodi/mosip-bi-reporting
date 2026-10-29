import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { RID_CONNU, afficher, simulerApi } from '../../test/apiSimulee';
import { SuiviDossierBouton } from './SuiviDossier';

const texte = (t: string) => t.replace(/\s+/g, ' ');
const appelsSuivi = (appels: URL[]) => appels.filter((u) => u.pathname.endsWith('/enrolement/suivi'));

/**
 * Le bouton et sa fenêtre seuls, sans la page Enrôlement et ses graphiques : la fenêtre ne dépend d'aucun bloc, et la
 * page complète rendait ces tests lents sur le serveur (délai dépassé le 29/10/2026).
 */
async function ouvrir() {
  const utilisateur = userEvent.setup();
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <SuiviDossierBouton />
    </QueryClientProvider>,
  );
  await utilisateur.click(screen.getByRole('button', { name: 'Suivre un dossier' }));
  const fenetre = within(await screen.findByRole('dialog', { name: 'Suivre un dossier' }));
  return { utilisateur, fenetre };
}

describe('Suivre un dossier', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('le bouton est dans le bandeau de la page Enrôlement', async () => {
    simulerApi();
    afficher('/enrolement');

    const bandeau = within(await screen.findByRole('region', { name: 'Enrôlement' }));
    expect(bandeau.getByRole('button', { name: 'Suivre un dossier' })).toBeInTheDocument();
  });

  it('un RID mal formé est refusé sans appeler l’API', async () => {
    const appels = simulerApi();
    const { utilisateur, fenetre } = await ouvrir();

    await utilisateur.type(fenetre.getByLabelText('Numéro d’inscription (RID)'), '2010110023');
    await utilisateur.click(fenetre.getByRole('button', { name: 'Rechercher' }));

    expect(fenetre.getByRole('alert')).toHaveTextContent('Le RID compte 29 chiffres.');
    expect(appelsSuivi(appels)).toHaveLength(0);
  });

  it('un RID connu : le RID part dans le corps, le champ est vidé, le résultat ne le montre pas', async () => {
    const appels = simulerApi();
    const { utilisateur, fenetre } = await ouvrir();
    const fetchSimule = vi.mocked(globalThis.fetch);

    // Collé avec des espaces : seuls les chiffres sont gardés.
    await utilisateur.type(
      fenetre.getByLabelText('Numéro d’inscription (RID)'),
      `${RID_CONNU.slice(0, 10)} ${RID_CONNU.slice(10)}`,
    );
    await utilisateur.click(fenetre.getByRole('button', { name: 'Rechercher' }));

    expect(await fenetre.findByText(/^En cours · sans activité depuis \d+ jours$/)).toBeInTheDocument();
    const [url, init] = fetchSimule.mock.calls.find(([u]) => String(u).endsWith('/enrolement/suivi'))!;
    expect(String(url)).not.toContain(RID_CONNU);
    expect(init).toMatchObject({ method: 'POST', body: JSON.stringify({ rid: RID_CONNU }) });
    expect(appelsSuivi(appels)).toHaveLength(1);

    const dialogue = screen.getByRole('dialog');
    expect(dialogue).not.toHaveTextContent(RID_CONNU);
    expect(fenetre.getByText('Nouvelle inscription')).toBeInTheDocument();
    expect(fenetre.getByText('EPP Doumassesse I G/B')).toBeInTheDocument();
    expect(fenetre.getByText('Golfe, Grand Lomé')).toBeInTheDocument();
    // L'étape en cours (le dossier n'est ni rejeté ni échoué), le motif de MOSIP et son message type (en anglais).
    expect(fenetre.getByText('Étape en cours')).toBeInTheDocument();
    expect(fenetre.getByText('En file d’attente de vérification manuelle')).toBeInTheDocument();
    expect(fenetre.getByText('Manual verification Sent to queue')).toHaveAttribute('lang', 'en');
    const jalons = within(fenetre.getByRole('list', { name: 'Jalons du dossier' })).getAllByRole('listitem');
    expect(jalons.map((j) => j.querySelector('.jalon__libelle')?.firstChild?.textContent)).toEqual([
      'Enrôlé au poste',
      'Synchronisé avec MOSIP',
      'Reçu par MOSIP',
      'Vérification manuelle',
      'NIU généré',
    ]);
    expect(jalons[0]).toHaveTextContent(texte('02/09/2026 à 10h14'));
    expect(jalons[3]).toHaveTextContent('(étape actuelle)');

    // Nouvelle recherche : le champ revient, vide.
    await utilisateur.click(fenetre.getByRole('button', { name: 'Nouvelle recherche' }));
    expect(fenetre.getByLabelText('Numéro d’inscription (RID)')).toHaveValue('');
  });

  it('un RID inconnu : message en rouge adouci, sans le RID', async () => {
    simulerApi();
    const { utilisateur, fenetre } = await ouvrir();

    const champ = fenetre.getByLabelText('Numéro d’inscription (RID)');
    await utilisateur.type(champ, '9'.repeat(29));
    await utilisateur.click(fenetre.getByRole('button', { name: 'Rechercher' }));

    expect(await fenetre.findByRole('alert')).toHaveTextContent(
      'Ce RID ne correspond à aucun dossier ou paquet.',
    );
    expect(champ).toHaveValue('');
    expect(screen.getByRole('dialog')).not.toHaveTextContent('9'.repeat(29));
  });

  it('se ferme avec Échap ou la croix ; à la réouverture, rien n’est gardé', async () => {
    simulerApi();
    const { utilisateur, fenetre } = await ouvrir();

    await utilisateur.type(fenetre.getByLabelText('Numéro d’inscription (RID)'), '123');
    await utilisateur.keyboard('{Escape}');
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());

    await utilisateur.click(screen.getByRole('button', { name: 'Suivre un dossier' }));
    const rouverte = within(await screen.findByRole('dialog', { name: 'Suivre un dossier' }));
    expect(rouverte.getByLabelText('Numéro d’inscription (RID)')).toHaveValue('');
    await utilisateur.click(rouverte.getByRole('button', { name: 'Fermer' }));
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  });
});
