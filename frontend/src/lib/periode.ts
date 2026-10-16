/**
 * Filtre Période des pages (règle validée sur la maquette) : les périodes relatives se terminent à la dernière
 * donnée de la page, et une période personnalisée est bornée aux données disponibles.
 */
export const CHOIX_PERIODE = ['tout', '7j', '30j', '90j', 'perso'] as const;
export type ChoixPeriode = (typeof CHOIX_PERIODE)[number];

export const LIBELLES_PERIODE: Record<ChoixPeriode, string> = {
  tout: 'Depuis le début',
  '7j': '7 derniers jours',
  '30j': '30 derniers jours',
  '90j': '90 derniers jours',
  perso: 'Période personnalisée',
};

/** Dates ISO « aaaa-mm-jj », bornes incluses. */
export interface Plage {
  du: string;
  au: string;
}

const JOURS: Partial<Record<ChoixPeriode, number>> = { '7j': 7, '30j': 30, '90j': 90 };

const versDate = (iso: string) => new Date(`${iso}T00:00:00Z`);
const versIso = (date: Date) => date.toISOString().slice(0, 10);
const borner = (iso: string, min: string, max: string) => (iso < min ? min : iso > max ? max : iso);

export function estChoixPeriode(valeur: unknown): valeur is ChoixPeriode {
  return typeof valeur === 'string' && (CHOIX_PERIODE as readonly string[]).includes(valeur);
}

/**
 * Calcule la plage de dates d'un choix de période.
 * @param donnees première et dernière date disponibles pour la page
 * @param perso dates saisies pour une période personnalisée
 */
export function plagePeriode(choix: ChoixPeriode, donnees: Plage, perso: Partial<Plage> = {}): Plage {
  const jours = JOURS[choix];
  if (jours) {
    const debut = versDate(donnees.au);
    debut.setUTCDate(debut.getUTCDate() - (jours - 1));
    return { du: borner(versIso(debut), donnees.du, donnees.au), au: donnees.au };
  }
  if (choix === 'perso') {
    let du = borner(perso.du ?? donnees.du, donnees.du, donnees.au);
    let au = borner(perso.au ?? donnees.au, donnees.du, donnees.au);
    if (du > au) [du, au] = [au, du];
    return { du, au };
  }
  return { ...donnees };
}
