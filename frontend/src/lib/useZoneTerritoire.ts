import { useNavigate, useSearch } from '@tanstack/react-router';
import type { FiltresUrl } from './filtresUrl';

/**
 * Zone ouverte dans le bloc Territoire de l'Enrôlement, à tout niveau (région, préfecture, commune, canton, localité,
 * centre), lue dans l'adresse (?zone=10011). Un ancien lien ?region=KAR ouvre toujours la région. Seul ce bloc la
 * suit ; l'API vérifie le code (zone inconnue : 404).
 */
export function useZoneTerritoire(): {
  /** Code bi.zone de la zone ouverte, undefined pour le Togo. */
  code?: string;
  /** Ouvre une zone (ou revient au Togo), sans faire remonter la page. */
  choisir: (code: string | undefined, options?: { historique?: boolean }) => void;
} {
  const filtres: FiltresUrl = useSearch({ strict: false });
  const naviguer = useNavigate();
  const code = filtres.zone ?? filtres.region;

  const choisir = (nouveau: string | undefined, options: { historique?: boolean } = {}) =>
    naviguer({
      to: '.',
      search: (precedent: FiltresUrl) => ({ ...precedent, zone: nouveau, region: undefined }),
      replace: !options.historique,
      // Le clic vient du bloc Territoire, en bas de page : la page ne remonte pas.
      resetScroll: false,
    });

  return { code, choisir };
}
