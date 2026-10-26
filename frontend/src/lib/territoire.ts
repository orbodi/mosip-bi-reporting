import { nf, part, pct } from './format';

/**
 * Règles d'affichage du bloc Territoire (maquette Enrôlement) : couleur de la carte selon le taux de NIU générés,
 * alerte sur le taux de rejet. Les taux sont calculés ici, à partir des nombres bruts de l'API.
 */

/** Seuil de l'alerte ▲ : taux de rejet de 3,5 % ou plus, arrondi à une décimale comme à l'affichage. */
export const SEUIL_ALERTE_REJET = 3.5;

/** Classes de couleur de la carte (taux de NIU générés), de la plus claire à la plus foncée. */
export const CLASSES_TAUX_NIU = [
  { borne: 0.92, libelle: '< 92 %', jeton: '--seq-1' },
  { borne: 0.93, libelle: '92 à 93 %', jeton: '--seq-2' },
  { borne: 0.94, libelle: '93 à 94 %', jeton: '--seq-3' },
  { borne: Number.POSITIVE_INFINITY, libelle: '94 % et +', jeton: '--seq-4' },
] as const;

export interface ChiffresZone {
  inscriptions: number;
  niuGeneres: number;
  rejetees: number;
}

/** Part des inscriptions qui ont leur NIU (NaN sans inscription). */
export function tauxNiu(z: ChiffresZone): number {
  return part(z.niuGeneres, z.inscriptions);
}

/** Part des inscriptions rejetées (NaN sans inscription). */
export function tauxRejet(z: ChiffresZone): number {
  return part(z.rejetees, z.inscriptions);
}

/** Indice de la classe de couleur d'un taux de NIU, ou -1 sans inscription (zone grisée). */
export function classeTauxNiu(taux: number): number {
  if (!Number.isFinite(taux)) return -1;
  return CLASSES_TAUX_NIU.findIndex((c) => taux < c.borne);
}

/** Vrai si le taux de rejet, arrondi à une décimale, atteint 3,5 %. */
export function alerteRejet(z: ChiffresZone): boolean {
  const taux = tauxRejet(z);
  return Number.isFinite(taux) && Math.round(taux * 1000) / 10 >= SEUIL_ALERTE_REJET;
}

/** Nom comparable d'une zone : sans accents, casse ni ponctuation (« Tône » = « tone », « Grand Lomé » = « grandlome »). */
export function cleNom(nom: string): string {
  return nom
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '');
}

/** Lecture d'une zone (carte) : « Kara : 92,6 % de NIU générés, 386 004 inscriptions ». */
export function lectureZone(nom: string, z: ChiffresZone): string {
  if (z.inscriptions === 0) return `${nom} : aucune inscription sur la période`;
  return `${nom} : ${pct(tauxNiu(z))} de NIU générés, ${nf(z.inscriptions)} inscriptions`;
}

/** Niveaux de l'arborescence bi.zone, de la région au centre d'enrôlement. */
const NIVEAUX: Record<string, { nom: string; pluriel: string; de: string }> = {
  region: { nom: 'région', pluriel: 'régions', de: 'de la région' },
  prefecture: { nom: 'préfecture', pluriel: 'préfectures', de: 'de la préfecture' },
  commune: { nom: 'commune', pluriel: 'communes', de: 'de la commune' },
  canton: { nom: 'canton', pluriel: 'cantons', de: 'du canton' },
  localite: { nom: 'localité', pluriel: 'localités', de: 'de la localité' },
  centre: { nom: 'centre', pluriel: 'centres', de: 'du centre' },
};
const AUTRE = { nom: 'zone', pluriel: 'sous-zones', de: 'de la zone' };
const niveau = (code?: string | null) => (code && NIVEAUX[code]) || AUTRE;
const majuscule = (texte: string) => texte.charAt(0).toUpperCase() + texte.slice(1);

/** « région », « préfecture »… (« zone » pour un niveau inconnu). */
export function nomNiveau(code?: string | null): string {
  return niveau(code).nom;
}

/** Titre du bloc : « Territoire : vue nationale », « Territoire : région Savanes », « Territoire : canton Nano ». */
export function titreTerritoire(niveauZone: string | null | undefined, nom: string | undefined): string {
  return nom ? `Territoire : ${nomNiveau(niveauZone)} ${nom}` : 'Territoire : vue nationale';
}

/**
 * Légende du tableau des sous-zones : « Régions », « Préfectures de la région Savanes », « Localités du canton
 * Nano » ; « Sous-zones du canton Nano » quand les lignes mêlent deux niveaux (un centre rattaché au canton).
 */
export function legendeSousZones(
  niveauZone: string | null | undefined,
  nom: string | undefined,
  niveauxLignes: string[],
): string {
  const distincts = [...new Set(niveauxLignes)];
  const lignes = distincts.length === 1 ? niveau(distincts[0]) : AUTRE;
  if (!nom) return majuscule(lignes.pluriel);
  return `${majuscule(lignes.pluriel)} ${niveau(niveauZone).de} ${nom}`;
}

/**
 * En-tête de la colonne des noms du tableau : le niveau des lignes (« Région », « Préfecture », « Commune »…), ou
 * « Zone » quand elles mêlent deux niveaux (un centre rattaché directement au canton).
 */
export function enTeteNiveau(niveauxLignes: string[]): string {
  const distincts = [...new Set(niveauxLignes)];
  return distincts.length === 1 && NIVEAUX[distincts[0]] ? majuscule(NIVEAUX[distincts[0]].nom) : 'Zone';
}

/** « localités », « cantons »… ou « sous-zones » quand les lignes mêlent deux niveaux. */
export function nomPluriel(niveauxLignes: string[]): string {
  const distincts = [...new Set(niveauxLignes)];
  return distincts.length === 1 ? niveau(distincts[0]).pluriel : AUTRE.pluriel;
}

/** « 1 localité » ou « 12 localités » (« sous-zones » quand les niveaux sont mêlés). */
export function compteZones(nombre: number, niveauxLignes: string[]): string {
  const distincts = [...new Set(niveauxLignes)];
  const n = distincts.length === 1 ? niveau(distincts[0]) : AUTRE;
  return `${nombre} ${nombre > 1 ? n.pluriel : n === AUTRE ? 'sous-zone' : n.nom}`;
}

export interface LigneTerritoire extends ChiffresZone {
  inscriptions: number;
  preinscriptions: number;
}

/**
 * Lignes du tableau Territoire. Les régions et les préfectures gardent l'ordre du référentiel (du nord au sud) ; plus
 * bas, les sous-zones sont triées par inscriptions (beaucoup de localités, sans ordre géographique). Une sous-zone
 * sans inscription ni pré-inscription sur la période est masquée et seulement comptée (le référentiel MOSIP garde
 * des lieux inactifs). Sans réponse de l'API, toutes les zones attendues restent, chiffres à 0.
 */
export function lignesDuTableau<T extends LigneTerritoire>(
  lignes: T[],
  niveauZone: string | null | undefined,
  { masquerVides }: { masquerVides: boolean },
): { visibles: T[]; vides: T[] } {
  const vide = (l: T) => !(l.inscriptions > 0) && !(l.preinscriptions > 0);
  const visibles = masquerVides ? lignes.filter((l) => !vide(l)) : [...lignes];
  const vides = masquerVides ? lignes.filter(vide) : [];
  if (niveauZone && niveauZone !== 'region') visibles.sort((a, b) => b.inscriptions - a.inscriptions);
  return { visibles, vides };
}

/** Vrai si les pré-inscriptions ont un sens pour ces lignes : elles sont situées à la préfecture de résidence. */
export function avecPreinscriptions(niveauZone: string | null | undefined): boolean {
  return !niveauZone || niveauZone === 'region';
}
