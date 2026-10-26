/**
 * Pagination des tableaux de zones (bloc Territoire, Exploration) : beaucoup de cantons et de localités. Pages
 * numérotées à partir de 0 ; une page hors limites est ramenée à la dernière (le tableau a pu raccourcir).
 */
export const TAILLES_PAGE = [10, 20] as const;
export type TaillePage = (typeof TAILLES_PAGE)[number];

export interface PageDeLignes<T> {
  lignes: T[];
  /** Page affichée, de 0 à pages - 1. */
  page: number;
  pages: number;
  /** Rang (à partir de 1) de la première et de la dernière ligne affichées ; 0 et 0 sans ligne. */
  debut: number;
  fin: number;
  total: number;
}

export function paginer<T>(lignes: T[], page: number, taille: number): PageDeLignes<T> {
  const total = lignes.length;
  const pages = Math.max(1, Math.ceil(total / taille));
  const p = Math.min(Math.max(0, Math.floor(page)), pages - 1);
  const morceau = lignes.slice(p * taille, (p + 1) * taille);
  return {
    lignes: morceau,
    page: p,
    pages,
    debut: total === 0 ? 0 : p * taille + 1,
    fin: p * taille + morceau.length,
    total,
  };
}

/**
 * Numéros de page à afficher : la première, la dernière, la page courante et ses voisines ; « … » pour un trou de
 * plus d'une page. Ex. page 6 sur 14 (de 0) : 1, …, 6, 7, 8, …, 14 (affichés à partir de 1).
 */
export function numerosDePage(page: number, pages: number): (number | '…')[] {
  const gardes = new Set([0, pages - 1, page - 1, page, page + 1].filter((n) => n >= 0 && n < pages));
  const tries = [...gardes].sort((a, b) => a - b);
  const resultat: (number | '…')[] = [];
  tries.forEach((n, i) => {
    const precedent = tries[i - 1];
    if (precedent !== undefined && n - precedent === 2) resultat.push(precedent + 1);
    else if (precedent !== undefined && n - precedent > 2) resultat.push('…');
    resultat.push(n);
  });
  return resultat;
}
