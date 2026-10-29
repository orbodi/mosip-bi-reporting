import type { SuiviDossier } from '../api/client';
import { ErreurApi } from '../api/client';
import { miseAJourFr, nf } from './format';

/** Le RID : 29 chiffres (SuiviService.FORMAT_RID). */
export const LONGUEUR_RID = 29;
export const MESSAGE_FORMAT = 'Le RID compte 29 chiffres.';
export const MESSAGE_INTROUVABLE = 'Ce RID ne correspond à aucun dossier ou paquet.';

/** Ne garde que les chiffres (un RID collé avec des espaces ou des tirets), 29 au plus. */
export function nettoyerRid(saisie: string): string {
  return saisie.replace(/\D/g, '').slice(0, LONGUEUR_RID);
}

export const ridValide = (rid: string) => new RegExp(`^\\d{${LONGUEUR_RID}}$`).test(rid);

/** Message à afficher pour une recherche en échec ; jamais le RID. */
export function messageErreur(erreur: unknown): string {
  if (erreur instanceof ErreurApi) {
    if (erreur.statut === 404) return MESSAGE_INTROUVABLE;
    if (erreur.statut === 400) return MESSAGE_FORMAT;
    if (erreur.statut === 503) return 'Le suivi d’un dossier n’est pas disponible pour le moment.';
  }
  return 'La recherche n’a pas abouti. Réessayez dans un instant.';
}

export type TonDevenir = 'niu' | 'en-cours' | 'bloque' | 'echoue' | 'rejete' | 'non-classe';

const DEVENIRS: Record<string, { libelle: string; ton: TonDevenir }> = {
  niu: { libelle: 'NIU généré', ton: 'niu' },
  en_cours: { libelle: 'En cours', ton: 'en-cours' },
  echoue: { libelle: 'Échoué', ton: 'echoue' },
  rejete: { libelle: 'Rejeté', ton: 'rejete' },
  non_classe: { libelle: 'Non classé', ton: 'non-classe' },
  non_recu: { libelle: 'Synchronisé, pas encore reçu', ton: 'en-cours' },
};

const JOUR_MS = 86_400_000;

/** Jours entiers depuis la dernière activité (au moins 0). */
export function joursDepuis(depuis: string, maintenant = new Date()): number {
  return Math.max(0, Math.floor((maintenant.getTime() - new Date(depuis).getTime()) / JOUR_MS));
}

/** Pastille d'état : « En cours · sans activité depuis 41 jours » pour un dossier bloqué. */
export function etatDossier(d: SuiviDossier, maintenant = new Date()): { libelle: string; ton: TonDevenir } {
  const base = DEVENIRS[d.devenir] ?? { libelle: 'Non classé', ton: 'non-classe' as const };
  if (d.devenir === 'en_cours' && d.bloque) {
    const depuis = d.derniereActiviteLe
      ? `depuis ${nf(joursDepuis(d.derniereActiviteLe, maintenant))} jours`
      : 'depuis plus de 30 jours';
    return { libelle: `En cours · sans activité ${depuis}`, ton: 'bloque' };
  }
  return base;
}

/**
 * Intitulé de l'étape : « Arrêté à l'étape » seulement pour un dossier rejeté ou échoué (le traitement s'arrête là),
 * « Dernière étape » pour un NIU, « Étape en cours » sinon (un dossier en cours avance, même lentement).
 */
export function intituleEtape(devenir: string): string {
  if (devenir === 'rejete' || devenir === 'echoue') return 'Arrêté à l’étape';
  if (devenir === 'niu') return 'Dernière étape';
  return 'Étape en cours';
}

const TYPES: Record<string, string> = {
  NEW: 'Nouvelle inscription',
  UPDATE: 'Mise à jour',
  LOST: 'NIU perdu',
  RES_UPDATE: 'Mise à jour par la personne',
};

/** Type de demande en français ; un code inconnu garde son code (jamais deviné). */
export const typeDemande = (code: string) => TYPES[code] ?? `Demande ${code}`;

const STATUTS: Record<string, string> = {
  SUCCESS: 'Réussie',
  PROCESSED: 'Réussie',
  FAILED: 'Échouée',
  ERROR: 'Erreur',
  REJECTED: 'Rejetée',
  IN_PROGRESS: 'En cours',
  PROCESSING: 'En cours',
  REPROCESS: 'À retraiter',
};

/** Statut de la dernière transaction en français, null si inconnu. */
export const statutEtape = (statut?: string | null) => (statut ? (STATUTS[statut] ?? statut) : null);

export interface Jalon {
  cle: string;
  libelle: string;
  /** « 02/09/2026 à 10h14 », ou ce qui en tient lieu ; « — » pour un jalon à venir. */
  quand: string;
  /** fait, étape en cours, à venir, refus au poste, arrêt définitif (rejeté, échoué : pas de NIU à venir). */
  etat: 'fait' | 'actuel' | 'a-venir' | 'refus' | 'arret';
}

const quand = (date?: string | null) => (date ? miseAJourFr(date) : 'date inconnue');

/**
 * Jalons du dossier, du poste au NIU : enrôlé, synchronisé, refusé au poste (s'il l'a été), reçu par MOSIP, puis le
 * NIU ; ou l'étape en cours et le NIU à venir ; ou, pour un dossier rejeté ou échoué, l'étape où il s'est arrêté.
 */
export function jalonsDossier(d: SuiviDossier): Jalon[] {
  const j = d.jalons;
  const liste: Jalon[] = [
    { cle: 'enrole', libelle: 'Enrôlé au poste', quand: quand(j.enroleLe), etat: 'fait' },
    {
      cle: 'synchronise',
      libelle: 'Synchronisé avec MOSIP',
      quand: j.synchroniseLe ? quand(j.synchroniseLe) : j.recuLe ? 'date inconnue' : '—',
      etat: j.synchroniseLe || j.recuLe ? 'fait' : 'a-venir',
    },
  ];
  if (j.refusPoste) liste.push({ cle: 'refus', libelle: 'Refusé au poste', quand: '', etat: 'refus' });
  if (!j.recuLe) {
    liste.push({ cle: 'recu', libelle: 'Reçu par MOSIP', quand: '—', etat: 'actuel' });
    liste.push({ cle: 'niu', libelle: 'NIU généré', quand: '—', etat: 'a-venir' });
    return liste;
  }
  liste.push({ cle: 'recu', libelle: 'Reçu par MOSIP', quand: quand(j.recuLe), etat: 'fait' });
  if (d.devenir === 'niu') {
    liste.push({ cle: 'niu', libelle: 'NIU généré', quand: quand(j.niuLe), etat: 'fait' });
    return liste;
  }
  const arret = d.devenir === 'rejete' || d.devenir === 'echoue';
  liste.push({
    cle: 'etape',
    libelle: d.etape?.libelle ?? 'Traitement par MOSIP',
    quand: d.derniereActiviteLe
      ? `${arret ? 'arrêté le' : 'dernière activité le'} ${miseAJourFr(d.derniereActiviteLe)}`
      : '',
    etat: arret ? 'arret' : 'actuel',
  });
  // Rejeté ou échoué : le traitement s'arrête là, aucun NIU n'est attendu.
  if (!arret) liste.push({ cle: 'niu', libelle: 'NIU généré', quand: '—', etat: 'a-venir' });
  return liste;
}
