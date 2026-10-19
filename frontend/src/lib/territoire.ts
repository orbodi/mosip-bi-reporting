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
  if (!Number.isFinite(z.inscriptions)) return `${nom} : chiffres indisponibles`;
  if (z.inscriptions === 0) return `${nom} : aucune inscription sur la période`;
  return `${nom} : ${pct(tauxNiu(z))} de NIU générés, ${nf(z.inscriptions)} inscriptions`;
}
