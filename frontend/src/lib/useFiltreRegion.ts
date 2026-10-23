import { useNavigate, useSearch } from '@tanstack/react-router';
import type { Region } from '../api/client';
import { useRegions } from '../api/meta';
import type { FiltresUrl } from './filtresUrl';

/**
 * Région des pages de vue d'ensemble. Deux notions distinctes :
 * - la portée de l'utilisateur : un utilisateur régional n'a qu'une région (liste de l'API), toujours appliquée ;
 *   un utilisateur national n'en a pas, et tous les blocs restent nationaux ;
 * - la zone ouverte dans le bloc géographique de la page (Territoire, carte), lue dans l'adresse (?region=KAR) :
 *   seul ce bloc la suit (préfectures de la région). Tant que la liste des régions n'est pas chargée, le code de
 *   l'adresse est transmis tel quel (l'API le vérifie) ; ensuite, un code absent de la liste est ignoré.
 */
export function useFiltreRegion(): {
  regions: Region[];
  /** Zone ouverte dans le bloc géographique (ou la région d'un utilisateur régional), undefined pour le Togo. */
  region?: Region;
  /** Code de cette zone, à passer à l'API du bloc géographique (paramètre zone). */
  code?: string;
  /** Région imposée à un utilisateur régional, undefined pour un utilisateur national : suivie par tous les blocs. */
  portee?: Region;
  /** Vrai pour un utilisateur régional (une seule région proposée par l'API). */
  regional: boolean;
  /** Ouvre une région (ou revient au Togo) dans le bloc géographique, sans faire remonter la page. */
  choisir: (code: string | undefined, options?: { historique?: boolean }) => void;
} {
  const filtres: FiltresUrl = useSearch({ strict: false });
  const naviguer = useNavigate();
  const { data } = useRegions();
  const regions = data ?? [];

  const regional = regions.length === 1;
  const region = regional ? regions[0] : regions.find((r) => r.code === filtres.region);
  const code = data ? region?.code : filtres.region;

  const choisir = (nouveau: string | undefined, options: { historique?: boolean } = {}) =>
    naviguer({
      to: '.',
      search: (precedent: FiltresUrl) => ({ ...precedent, region: nouveau }),
      replace: !options.historique,
      // Ouvrir une région ne fait pas remonter la page (le clic vient du bloc Territoire, en bas de page).
      resetScroll: false,
    });

  return { regions, region, code, portee: regional ? regions[0] : undefined, regional, choisir };
}
