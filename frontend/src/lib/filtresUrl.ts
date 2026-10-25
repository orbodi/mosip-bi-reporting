import type { ChoixPeriode } from './periode';

/** Filtres communs portés par l'adresse : une vue filtrée se partage par lien. */
export interface FiltresUrl {
  /** Toujours absents depuis le retrait du filtre Période (voir validerFiltres) : toutes les données. */
  periode?: ChoixPeriode;
  du?: string;
  au?: string;
  /** Région ouverte dans le bloc géographique d'une page (code bi.zone), absente pour le Togo. */
  region?: string;
  /** Zone ouverte dans le bloc Territoire de l'Enrôlement, à tout niveau (code bi.zone), absente pour le Togo. */
  zone?: string;
}

/** Même règle que le paramètre « zone » de l'API. */
const CODE_ZONE = /^[A-Za-z0-9_-]{1,40}$/;

/**
 * Filtres retenus dans l'adresse. Les pages de vue d'ensemble n'ont plus de filtre Période : une période venue d'un
 * ancien lien (?periode=7j, ?du=…) est écartée, pour que les blocs ne soient jamais filtrés sans filtre visible.
 * L'Exploration garde ses filtres dans la page. Seule la zone ouverte dans le bloc géographique reste (?region=KAR,
 * ou ?zone=10011 pour le bloc Territoire de l'Enrôlement).
 */
export function validerFiltres(recherche: Record<string, unknown>): FiltresUrl {
  const code = (valeur: unknown) =>
    typeof valeur === 'string' && CODE_ZONE.test(valeur) ? valeur : undefined;
  return { region: code(recherche.region), zone: code(recherche.zone) };
}
