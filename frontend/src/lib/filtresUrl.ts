import { estChoixPeriode, type ChoixPeriode } from './periode';

/** Filtres communs portés par l'adresse : une vue filtrée se partage par lien. */
export interface FiltresUrl {
  periode?: ChoixPeriode;
  du?: string;
  au?: string;
  /** Code de la région du filtre Région (bi.zone), absent pour toutes les régions. */
  region?: string;
}

const DATE_ISO = /^\d{4}-\d{2}-\d{2}$/;
/** Même règle que le paramètre « zone » de l'API. */
const CODE_ZONE = /^[A-Za-z0-9_-]{1,40}$/;

export function validerFiltres(recherche: Record<string, unknown>): FiltresUrl {
  const date = (valeur: unknown) =>
    typeof valeur === 'string' && DATE_ISO.test(valeur) ? valeur : undefined;
  return {
    periode: estChoixPeriode(recherche.periode) ? recherche.periode : undefined,
    du: date(recherche.du),
    au: date(recherche.au),
    region:
      typeof recherche.region === 'string' && CODE_ZONE.test(recherche.region) ? recherche.region : undefined,
  };
}
