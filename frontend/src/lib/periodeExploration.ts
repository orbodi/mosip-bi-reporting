import type { Plage } from './periode';
import { dateFr } from './format';

/**
 * Filtre Période de l'Exploration (décisions du 05/11/2026 : option « Personnalisée », raccourcis). Valeur du filtre :
 * « tout », « A:aaaa » (une année), « M:aaaa-mm » (un mois), « P:aaaa-mm-jj:aaaa-mm-jj » (période personnalisée,
 * fin vide = un seul jour) ou « R:<raccourci> » (30 derniers jours, mois en cours, mois précédent, année en cours,
 * comptés jusqu'à la dernière donnée de la source). Les dates sont bornées aux données de la source.
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

/** Raccourcis de la liste Période, dans l'ordre affiché. */
export const RACCOURCIS = [
  { id: 'R:30j', libelle: '30 derniers jours' },
  { id: 'R:mois', libelle: 'Mois en cours' },
  { id: 'R:moisprec', libelle: 'Mois précédent' },
  { id: 'R:annee', libelle: 'Année en cours' },
] as const;

export const estRaccourci = (periode: string) => RACCOURCIS.some((r) => r.id === periode);

const jourIso = (d: Date) => d.toISOString().slice(0, 10);
const decaler = (jour: string, jours: number) => {
  const d = new Date(`${jour}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + jours);
  return jourIso(d);
};

/** Plage d'un raccourci, comptée jusqu'à la dernière donnée de la source (bornes.au) ; undefined sans bornes. */
function plageRaccourci(periode: string, bornes?: Plage): Plage | undefined {
  if (!bornes) return undefined;
  const fin = bornes.au;
  const [a, m] = [Number(fin.slice(0, 4)), Number(fin.slice(5, 7))];
  if (periode === 'R:30j') return { du: decaler(fin, -29), au: fin };
  if (periode === 'R:mois') return { du: `${fin.slice(0, 7)}-01`, au: fin };
  if (periode === 'R:annee') return { du: `${a}-01-01`, au: fin };
  if (periode === 'R:moisprec') {
    return { du: jourIso(new Date(Date.UTC(a, m - 2, 1))), au: jourIso(new Date(Date.UTC(a, m - 1, 0))) };
  }
  return undefined;
}

/** Libellé d'un raccourci avec ses dates : « Mois précédent, du 01/10/2026 au 31/10/2026 ». */
export function libelleRaccourci(periode: string, bornes?: Plage): string {
  const nom = RACCOURCIS.find((r) => r.id === periode)?.libelle ?? periode;
  const plage = plageRaccourci(periode, bornes);
  return plage ? `${nom}, du ${dateFr(plage.du)} au ${dateFr(plage.au)}` : nom;
}

/**
 * Plage de dates demandée à l'API, ou undefined pour toute la période (ou une période personnalisée invalide, ou un
 * raccourci tant que les bornes de la source ne sont pas connues).
 */
export function plageExploration(periode: string, bornes?: Plage): Plage | undefined {
  if (estRaccourci(periode)) return plageRaccourci(periode, bornes);
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
