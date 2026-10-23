import type { ChoixPeriode } from './periode';

/** Filtres communs portés par l'adresse : une vue filtrée se partage par lien. */
export interface FiltresUrl {
  /** Toujours absents depuis le retrait du filtre Période (voir validerFiltres) : toutes les données. */
  periode?: ChoixPeriode;
  du?: string;
  au?: string;
  /** Région ouverte dans le bloc Territoire (code bi.zone), absente pour le Togo. */
  region?: string;
}

/** Même règle que le paramètre « zone » de l'API. */
const CODE_ZONE = /^[A-Za-z0-9_-]{1,40}$/;

/**
 * Filtres retenus dans l'adresse. Les pages de vue d'ensemble n'ont plus de filtre Période : une période venue d'un
 * ancien lien (?periode=7j, ?du=…) est écartée, pour que les blocs ne soient jamais filtrés sans filtre visible.
 * L'Exploration garde ses filtres dans la page. Seule la zone ouverte dans le bloc Territoire reste (?region=KAR).
 */
export function validerFiltres(recherche: Record<string, unknown>): FiltresUrl {
  return {
    region:
      typeof recherche.region === 'string' && CODE_ZONE.test(recherche.region) ? recherche.region : undefined,
  };
}
