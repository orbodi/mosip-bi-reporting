import { useNavigate, useSearch } from '@tanstack/react-router';
import type { Region } from '../api/client';
import { useRegions } from '../api/meta';
import type { FiltresUrl } from './filtresUrl';

/**
 * Filtre Région de la page, lu dans l'adresse (?region=KAR). Tant que la liste des régions n'est pas chargée, le
 * code de l'adresse est transmis tel quel (l'API le vérifie : 404 inconnu, 403 hors portée) ; ensuite, un code absent
 * de la liste est ignoré. Un utilisateur régional n'a qu'une région : elle est toujours appliquée.
 */
export function useFiltreRegion(): {
  regions: Region[];
  /** Région choisie, ou undefined pour toutes les régions. */
  region?: Region;
  /** Code à passer à l'API (paramètre zone). */
  code?: string;
  /** Vrai si un utilisateur national a choisi une région : les blocs qui ne suivent pas le filtre le signalent. */
  actif: boolean;
  /** Vrai pour un utilisateur régional (une seule région proposée par l'API). */
  regional: boolean;
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
      // Changer de région ne fait pas remonter la page (le clic peut venir du bloc Territoire, en bas de page).
      resetScroll: false,
    });

  return { regions, region, code, actif: !regional && !!code, regional, choisir };
}
