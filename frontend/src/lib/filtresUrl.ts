import { validerExploration, type RechercheExploration } from './etatExploration';
import type { ChoixPeriode } from './periode';

/** Filtres communs portés par l'adresse : une vue filtrée se partage par lien. */
export interface FiltresUrl extends RechercheExploration {
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
 * La zone ouverte dans le bloc géographique reste (?region=KAR, ou ?zone=10011 pour le bloc Territoire de
 * l'Enrôlement), ainsi que les choix de l'Exploration (lib/etatExploration, 05/11/2026).
 */
export function validerFiltres(recherche: Record<string, unknown>): FiltresUrl {
  // Le routeur lit « 10011 » comme un nombre : on le remet en texte.
  const code = (valeur: unknown) => {
    const v = typeof valeur === 'number' ? String(valeur) : valeur;
    return typeof v === 'string' && CODE_ZONE.test(v) ? v : undefined;
  };
  return { region: code(recherche.region), zone: code(recherche.zone), ...validerExploration(recherche) };
}

/** Filtres gardés en changeant de page : la zone ouverte, jamais les choix de l'Exploration. */
export const sansExploration = ({ region, zone }: FiltresUrl): FiltresUrl => ({ region, zone });
