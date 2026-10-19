import type { DevenirInscriptions, InscriptionsParSemaine, LigneZone, Territoire } from '../api/client';

/**
 * Données de remplacement quand l'API ne répond pas (ou pas encore) : les blocs gardent leur mise en page (cartes,
 * axes, carte, tableau) avec des valeurs inconnues. NaN s'affiche « – » (lib/format.ts) et ne colore rien : on ne
 * montre jamais de zéro inventé.
 */
const INCONNU = Number.NaN;

const chiffresInconnus = {
  inscriptions: INCONNU,
  niuGeneres: INCONNU,
  enCours: INCONNU,
  echouees: INCONNU,
  rejetees: INCONNU,
  nonClassees: INCONNU,
};

/** Vrai si un nombre de l'API est connu (faux pour les données de remplacement). */
export const estConnu = (n: number) => Number.isFinite(n);

export function devenirInconnu(perimetre = 'Ensemble du Togo'): DevenirInscriptions {
  return { perimetre, ...chiffresInconnus };
}

const versIso = (d: Date) => d.toISOString().slice(0, 10);

/**
 * Lundis des 12 semaines complètes qui finissent au plus tard le jour {@code fin} (« aaaa-mm-jj »), comme l'API
 * (EnrolementService.lundisDesSemainesCompletes).
 */
export function lundisDesSemainesCompletes(fin: string, nombre = 12): string[] {
  const jour = new Date(`${fin}T00:00:00Z`);
  const jourSemaine = (jour.getUTCDay() + 6) % 7; // 0 = lundi … 6 = dimanche
  const dernierLundi = new Date(jour);
  dernierLundi.setUTCDate(jour.getUTCDate() - (jourSemaine === 6 ? 6 : jourSemaine + 7));
  return Array.from({ length: nombre }, (_, k) => {
    const lundi = new Date(dernierLundi);
    lundi.setUTCDate(dernierLundi.getUTCDate() - 7 * (nombre - 1 - k));
    return versIso(lundi);
  });
}

export function semainesInconnues(fin: string, perimetre = 'Ensemble du Togo'): InscriptionsParSemaine {
  return {
    perimetre,
    niuDisponibles: true,
    semaines: lundisDesSemainesCompletes(fin).map((lundi) => ({
      lundi,
      dansLaPeriode: true,
      inscriptions: INCONNU,
      niuGeneres: INCONNU,
    })),
  };
}

/** Zones connues sans leurs chiffres (codes du filtre Région quand ils sont chargés, sinon les noms des contours). */
export function territoireInconnu(
  perimetre: string,
  zones: { code: string; nom: string }[],
  niveau: string,
): Territoire {
  const lignes: LigneZone[] = zones.map((z) => ({
    code: z.code,
    nom: z.nom,
    niveau,
    horsReferentiel: false,
    ...chiffresInconnus,
  }));
  return { perimetre, ...chiffresInconnus, lignes };
}
