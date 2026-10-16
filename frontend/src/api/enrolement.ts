import { keepPreviousData, useQuery } from '@tanstack/react-query';
import type { Plage } from '../lib/periode';
import { RAFRAICHISSEMENT_MS, lireApi, type DevenirInscriptions } from './client';

/**
 * Devenir des inscriptions (GET /api/v1/enrolement/devenir), relu toutes les 30 s : les chiffres suivent le
 * pipeline temps réel sans recharger la page. Sans plage, l'API prend toutes les données disponibles.
 */
export function useDevenirInscriptions(plage: Plage | undefined, active = true) {
  return useQuery({
    queryKey: ['enrolement', 'devenir', plage?.du ?? null, plage?.au ?? null],
    queryFn: () => lireApi<DevenirInscriptions>('/enrolement/devenir', { du: plage?.du, au: plage?.au }),
    enabled: active,
    refetchInterval: RAFRAICHISSEMENT_MS,
    // Pas de clignotement quand la période change : les anciens chiffres restent affichés pendant le chargement.
    placeholderData: keepPreviousData,
  });
}
