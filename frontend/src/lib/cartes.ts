import type {
  CartesEnAttente,
  ImpressionRemise,
  ImpressionsParSemaine,
  MotifAnnulation,
} from '../api/client';
import { depuisApi, estConnu, semainesVides, type SemaineValeurs } from './blocsVides';
import { nf, part, pct } from './format';

/**
 * Règles d'affichage de la page Impression des cartes (docs/indicateurs.md, section Impression des cartes ; lecture
 * cohorte du 03/11/2026 : commandes au jour de réception, cartes au jour d'expédition). Les parts sont calculées
 * ici, depuis les nombres bruts de l'API.
 */

/** Chiffres du bloc « Impression et remise » ; valeur inconnue (NaN, affichée 0) sans réponse ou sans source. */
export interface ChiffresImpression {
  demandes: number;
  envoyees: number;
  enAttente: number;
  rejetees: number;
  annulees: number;
  derniereRejetee?: string;
  expediees: number;
  remises: number;
  remisesHorsLigne: number;
  remisesEnLigne: number;
  remisesSupport: number;
  remisesAutre: number;
  aRemettre: number;
  delaiMedianJours: number;
}

export function chiffresImpression(api?: ImpressionRemise): ChiffresImpression {
  const a = api?.disponible ? api : undefined;
  return {
    demandes: depuisApi(a?.demandes),
    envoyees: depuisApi(a?.envoyees),
    enAttente: depuisApi(a?.enAttente),
    rejetees: depuisApi(a?.rejetees),
    annulees: depuisApi(a?.annulees),
    derniereRejetee: a?.derniereRejetee ?? undefined,
    expediees: depuisApi(a?.expediees),
    remises: depuisApi(a?.remises),
    remisesHorsLigne: depuisApi(a?.remisesHorsLigne),
    remisesEnLigne: depuisApi(a?.remisesEnLigne),
    remisesSupport: depuisApi(a?.remisesSupport),
    remisesAutre: depuisApi(a?.remisesAutre),
    aRemettre: depuisApi(a?.aRemettre),
    delaiMedianJours: depuisApi(a?.delaiMedianJours),
  };
}

/** Ligne des modes de remise : « Remises : 4 446 166 hors ligne · 197 370 en ligne · 32 par le support ». */
export function texteModesRemise(c: ChiffresImpression): string {
  const morceaux = [
    `${nf(c.remisesHorsLigne)} hors ligne`,
    `${nf(c.remisesEnLigne)} en ligne`,
    `${nf(c.remisesSupport)} par le support`,
  ];
  if (estConnu(c.remisesAutre) && c.remisesAutre > 0) morceaux.push(`${nf(c.remisesAutre)} sans mode connu`);
  return `Remises : ${morceaux.join(' · ')}`;
}

/** Nom court d'un motif d'annulation (code MOSIP), pour le détail de la carte « Annulées ». */
const MOTIF_COURT: Record<string, string> = {
  CANCEL_PHOTO: 'photo',
  CANCEL_SEX: 'sexe',
  CANCEL_NAME: 'nom',
  PERSONALIZATION_MANAGER_REPORTED_ERROR: 'personnalisation',
  NON_REPERTORIE: 'motif non répertorié',
};

/**
 * Détail de la carte « Annulées » : « Parmi les demandes : photo 643, sexe 36, nom 10, personnalisation 4 ». Les
 * annulées font partie des demandes (elles gardent leur statut dans MOSIP). Sans motif connu : « Parmi les demandes ».
 */
export function texteAnnulees(motifs: MotifAnnulation[] = []): string {
  const liste = motifs
    .filter((m) => m.demandes > 0)
    .map((m) => `${MOTIF_COURT[m.code] ?? m.libelle.toLowerCase()} ${nf(m.demandes)}`);
  return liste.length ? `Parmi les demandes : ${liste.join(', ')}` : 'Parmi les demandes';
}

/** Les 12 semaines du graphique : cartes imprimées (expédiées), demandes, rejetées et annulées. */
export const CLES_SEMAINES = ['imprimees', 'demandes', 'rejetees', 'annulees'] as const;

export function semainesCartes(api: ImpressionsParSemaine | undefined, fin: string): SemaineValeurs[] {
  if (!api?.semaines.length) return semainesVides(fin, [...CLES_SEMAINES]);
  return api.semaines.map((s) => ({
    lundi: s.lundi,
    valeurs: { imprimees: s.expediees, demandes: s.demandes, rejetees: s.rejetees, annulees: s.annulees },
  }));
}

/** Note sous le graphique des rejetées et annulées : totaux des 12 semaines. */
export function noteRejeteesAnnulees(semaines: SemaineValeurs[]): string {
  const somme = (cle: string) =>
    semaines.reduce((s, x) => s + (estConnu(x.valeurs[cle]) ? x.valeurs[cle] : 0), 0);
  const rejetees = somme('rejetees');
  const annulees = somme('annulees');
  const libelleRejetees = rejetees > 1 ? 'demandes rejetées' : 'demande rejetée';
  const libelleAnnulees = annulees > 1 ? 'annulées' : 'annulée';
  return `Sur ces 12 semaines : ${nf(rejetees)} ${libelleRejetees}, ${nf(annulees)} ${libelleAnnulees}.`;
}

/**
 * Classes de couleur de la carte « Cartes à remettre par région » (part des cartes expédiées qui restent à remettre),
 * de la plus claire à la plus foncée, comme la maquette.
 */
export const CLASSES_A_REMETTRE = [
  { borne: 0.35, libelle: '< 35 %' },
  { borne: 0.45, libelle: '35 à 45 %' },
  { borne: 0.52, libelle: '45 à 52 %' },
  { borne: Number.POSITIVE_INFINITY, libelle: '52 % et +' },
] as const;

/** Part des cartes expédiées qui restent à remettre (NaN sans carte expédiée). */
export const partARemettre = (z: { expediees: number; aRemettre: number }) => part(z.aRemettre, z.expediees);

/** Indice de la classe de couleur, ou -1 sans carte expédiée (zone grisée). */
export function classeARemettre(partZone: number): number {
  if (!Number.isFinite(partZone)) return -1;
  return CLASSES_A_REMETTRE.findIndex((c) => partZone < c.borne);
}

/** Alerte ▲ du tableau : plus de la moitié des cartes expédiées reste à remettre (part arrondie à une décimale). */
export function alerteARemettre(z: { expediees: number; aRemettre: number }): boolean {
  const p = partARemettre(z);
  return Number.isFinite(p) && Math.round(p * 1000) / 10 > 50;
}

/** Lecture d'une zone (carte) : « Kara : 24,1 % des cartes expédiées à remettre (12 034 cartes) ». */
export function lectureARemettre(nom: string, z: { expediees: number; aRemettre: number }): string {
  if (!estConnu(z.expediees)) return `${nom} : ${pct(Number.NaN)} des cartes expédiées à remettre`;
  if (z.expediees === 0) return `${nom} : aucune carte expédiée sur la période`;
  return `${nom} : ${pct(partARemettre(z))} des cartes expédiées à remettre (${nf(z.aRemettre)} cartes)`;
}

/** Libellés des tranches d'ancienneté des cartes à remettre (codes de l'API), dans l'ordre du bloc. */
export const TRANCHES_ATTENTE = [
  { code: 'moins_30j', libelle: 'Moins de 30 jours', couleur: 'bleu-pale' },
  { code: '30_90j', libelle: '30 à 90 jours', couleur: 'bleu-clair' },
  { code: '90_180j', libelle: '90 à 180 jours', couleur: 'serie-1' },
  { code: 'plus_180j', libelle: 'Plus de 180 jours', couleur: 'bleu-fonce' },
] as const;

/** Barres du bloc « Depuis quand ces cartes attendent » ; une tranche absente de la réponse reste inconnue. */
export function barresAttente(api?: CartesEnAttente) {
  return TRANCHES_ATTENTE.map((t) => ({
    libelle: t.libelle,
    couleur: t.couleur,
    valeur: depuisApi(api?.tranches.find((x) => x.code === t.code)?.cartes),
  }));
}

/** Note du bloc : « 1 219 599 cartes, soit 83,3 % des cartes à remettre, attendent depuis plus de six mois. » */
export function noteAttente(api?: CartesEnAttente): string {
  const plus = depuisApi(api?.tranches.find((t) => t.code === 'plus_180j')?.cartes);
  const total = depuisApi(api?.aRemettre);
  return `${nf(plus)} cartes, soit ${pct(part(plus, total))} des cartes à remettre, attendent depuis plus de six mois.`;
}

/**
 * Vue d'ensemble, « Le parcours par région » : part des inscrits qui ont reçu leur carte (cartes remises /
 * inscriptions de la région, mêmes bornes que la maquette). Sur toute la durée, les deux nombres portent sur les mêmes
 * dossiers ; sur une période, sur des dossiers différents (note de la frise).
 */
export const CLASSES_AVEC_CARTE = [
  { borne: 0.45, libelle: '< 45 %' },
  { borne: 0.5, libelle: '45 à 50 %' },
  { borne: 0.6, libelle: '50 à 60 %' },
  { borne: Number.POSITIVE_INFINITY, libelle: '60 % et +' },
] as const;

/** Indice de la classe de couleur, ou -1 sans inscription ou sans chiffre (zone grisée). */
export function classeAvecCarte(partZone: number): number {
  if (!Number.isFinite(partZone)) return -1;
  return CLASSES_AVEC_CARTE.findIndex((c) => partZone < c.borne);
}

/** Vrai si moins de la moitié des inscrits a reçu sa carte (mise en gras du tableau). */
export const moinsDeLaMoitie = (partZone: number) => Number.isFinite(partZone) && partZone < 0.5;
