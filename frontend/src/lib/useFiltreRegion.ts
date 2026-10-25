import { useNavigate, useSearch } from '@tanstack/react-router';
import type { Region } from '../api/client';
import { useRegions } from '../api/meta';
import type { FiltresUrl } from './filtresUrl';

/**
 * Région ouverte dans le bloc géographique d'une page de vue d'ensemble (carte des Cartes, de la Vue d'ensemble), lue
 * dans l'adresse (?region=KAR) : seul ce bloc la suit. Chaque utilisateur a accès à tout le Togo (décision du
 * 25/10/2026). Tant que la liste des régions n'est pas chargée, le code de l'adresse est transmis tel quel (l'API le
 * vérifie) ; ensuite, un code absent de la liste est ignoré.
 * Le bloc Territoire de l'Enrôlement descend plus bas (jusqu'aux centres) : voir useZoneTerritoire.
 */
export function useFiltreRegion(): {
  regions: Region[];
  /** Région ouverte, undefined pour le Togo. */
  region?: Region;
  /** Code de cette région, à passer à l'API du bloc géographique (paramètre zone). */
  code?: string;
  /** Ouvre une région (ou revient au Togo) dans le bloc géographique, sans faire remonter la page. */
  choisir: (code: string | undefined, options?: { historique?: boolean }) => void;
} {
  const filtres: FiltresUrl = useSearch({ strict: false });
  const naviguer = useNavigate();
  const { data } = useRegions();
  const regions = data ?? [];

  const region = regions.find((r) => r.code === filtres.region);
  const code = data ? region?.code : filtres.region;

  const choisir = (nouveau: string | undefined, options: { historique?: boolean } = {}) =>
    naviguer({
      to: '.',
      search: (precedent: FiltresUrl) => ({ ...precedent, region: nouveau }),
      replace: !options.historique,
      // Ouvrir une région ne fait pas remonter la page (le clic vient du bloc géographique, en bas de page).
      resetScroll: false,
    });

  return { regions, region, code, choisir };
}
