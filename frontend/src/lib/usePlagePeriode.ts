import { useSearch } from '@tanstack/react-router';
import { useFraicheur, type CodeSource } from '../api/meta';
import type { FiltresUrl } from './filtresUrl';
import { plagePeriode, type ChoixPeriode, type Plage } from './periode';

/**
 * Filtre Période de la page : choix lu dans l'adresse, données disponibles de la source, plage calculée.
 * Utilisé par le filtre du bandeau et par les blocs, pour que tous appliquent exactement la même plage.
 */
export function usePlagePeriode(source: CodeSource): { choix: ChoixPeriode; donnees?: Plage; plage?: Plage } {
  const filtres: FiltresUrl = useSearch({ strict: false });
  const { fraicheur } = useFraicheur(source);

  const choix: ChoixPeriode = filtres.periode ?? 'tout';
  const donnees =
    fraicheur?.premiereDonnee && fraicheur.derniereDonnee
      ? { du: fraicheur.premiereDonnee, au: fraicheur.derniereDonnee.slice(0, 10) }
      : undefined;
  const plage = donnees ? plagePeriode(choix, donnees, { du: filtres.du, au: filtres.au }) : undefined;
  return { choix, donnees, plage };
}

/**
 * Plage à envoyer à l'API par les blocs : aucune pour « Depuis le début » (l'API prend toutes les données), sinon la
 * plage calculée. {@code prete} reste faux tant que les bornes de la source ne sont pas connues.
 */
export function usePlageApi(source: CodeSource): { choix: ChoixPeriode; plage?: Plage; prete: boolean } {
  const { choix, plage } = usePlagePeriode(source);
  const depuisLeDebut = choix === 'tout';
  return { choix, plage: depuisLeDebut ? undefined : plage, prete: depuisLeDebut || !!plage };
}
