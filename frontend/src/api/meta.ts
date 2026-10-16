import { useQuery } from '@tanstack/react-query';
import { RAFRAICHISSEMENT_MS, lireApi, type Meta } from './client';

export type CodeSource = 'enrolement' | 'cartes' | 'abis' | 'idps' | 'authentifications';

export function useMeta() {
  return useQuery({
    queryKey: ['meta'],
    queryFn: () => lireApi<Meta>('/meta'),
    staleTime: 5 * 60_000,
    // La pastille « Dernière mise à jour » suit le pipeline temps réel.
    refetchInterval: RAFRAICHISSEMENT_MS,
  });
}

/** Fraîcheur d'une source, ou undefined tant que la méta n'est pas chargée. */
export function useFraicheur(source: CodeSource) {
  const requete = useMeta();
  return { ...requete, fraicheur: requete.data?.sources.find((s) => s.source === source) };
}
