import type { Plage } from './periode';
import { dateFr } from './format';

/**
 * Filtre Période de l'Exploration (décision du 05/11/2026 : option « Personnalisée »). Valeur du filtre :
 * « tout », « A:aaaa » (une année), « M:aaaa-mm » (un mois) ou « P:aaaa-mm-jj:aaaa-mm-jj » (période personnalisée,
 * fin vide = un seul jour). Les dates sont bornées aux données de la source.
 */
export const PERSONNALISEE = 'P';

export const estPersonnalisee = (periode: string) => periode.startsWith('P:');

/** Valeur d'une période personnalisée ; la fin vide désigne le seul jour du début. */
export const periodePersonnalisee = (du: string, au: string) => `P:${du}:${au}`;

/** Dates saisies d'une période personnalisée (chaînes vides si non saisies). */
export function datesPersonnalisees(periode: string): { du: string; au: string } {
  const [, du = '', au = ''] = periode.split(':');
  return { du, au };
}

/** Message d'erreur d'une période personnalisée, ou undefined si elle est utilisable. */
export function erreurPersonnalisee(periode: string, bornes?: Plage): string | undefined {
  const { du, au } = datesPersonnalisees(periode);
  if (!du) return 'Choisissez au moins la date de début.';
  if (au && au < du) return 'La date de fin doit suivre la date de début.';
  if (bornes && (du > bornes.au || (au || du) < bornes.du)) {
    return `Aucune donnée sur cette période : données du ${dateFr(bornes.du)} au ${dateFr(bornes.au)}.`;
  }
  return undefined;
}

/** Plage de dates demandée à l'API, ou undefined pour toute la période (ou une période personnalisée invalide). */
export function plageExploration(periode: string, bornes?: Plage): Plage | undefined {
  if (periode.startsWith('A:')) return { du: `${periode.slice(2)}-01-01`, au: `${periode.slice(2)}-12-31` };
  if (periode.startsWith('M:')) {
    const [a, m] = periode.slice(2).split('-').map(Number);
    return { du: `${periode.slice(2)}-01`, au: new Date(Date.UTC(a, m, 0)).toISOString().slice(0, 10) };
  }
  if (estPersonnalisee(periode) && !erreurPersonnalisee(periode, bornes)) {
    const { du, au } = datesPersonnalisees(periode);
    return { du, au: au || du };
  }
  return undefined;
}

/** Libellé d'une période personnalisée : « le 02/10/2026 » ou « du 02/10/2026 au 15/10/2026 ». */
export function libellePersonnalisee(periode: string): string {
  const { du, au } = datesPersonnalisees(periode);
  if (!du) return 'Période personnalisée';
  return !au || au === du ? `le ${dateFr(du)}` : `du ${dateFr(du)} au ${dateFr(au)}`;
}
