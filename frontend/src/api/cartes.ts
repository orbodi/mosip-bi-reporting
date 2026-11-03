import { keepPreviousData, useQuery } from '@tanstack/react-query';
import type { Plage } from '../lib/periode';
import {
  RAFRAICHISSEMENT_MS,
  lireApi,
  type AnnulationsParMotif,
  type CartesEnAttente,
  type ImpressionRemise,
  type ImpressionsParSemaine,
  type TerritoireCartes,
  type TopCentresCartes,
} from './client';

/**
 * Lecture d'un bloc de la page Impression des cartes (GET /api/v1/cartes/…), relue comme les autres pages : le
 * pipeline publie toutes les 5 minutes. Sans plage, l'API prend toutes les données ; sans zone, tout le Togo.
 */
function useBlocCartes<T>(ressource: string, plage: Plage | undefined, active: boolean, zone?: string) {
  const parametres = { du: plage?.du, au: plage?.au, zone };
  return useQuery({
    queryKey: ['cartes', ressource, parametres],
    queryFn: () => lireApi<T>(`/cartes/${ressource}`, parametres),
    enabled: active,
    refetchInterval: RAFRAICHISSEMENT_MS,
    placeholderData: keepPreviousData,
  });
}

/** Impression et remise : demandes par statut, annulées, cartes expédiées, remises, à remettre, délai. */
export function useImpression(plage: Plage | undefined, active = true, zone?: string) {
  return useBlocCartes<ImpressionRemise>('impression', plage, active, zone);
}

/** Demandes, cartes imprimées, rejetées et annulées des 12 semaines complètes. */
export function useSemainesCartes(plage: Plage | undefined, active = true) {
  return useBlocCartes<ImpressionsParSemaine>('semaines', plage, active);
}

/** Cartes expédiées, remises et à remettre de la zone et de ses sous-zones (régions, puis préfectures). */
export function useTerritoireCartes(plage: Plage | undefined, zone: string | undefined, active = true) {
  return useBlocCartes<TerritoireCartes>('territoire', plage, active, zone);
}

/** Cartes à remettre par temps écoulé depuis l'expédition. */
export function useAttenteCartes(plage: Plage | undefined, active = true) {
  return useBlocCartes<CartesEnAttente>('attente', plage, active);
}

/** Les cinq centres qui ont remis le plus de cartes. */
export function useTopCentresCartes(plage: Plage | undefined, active = true) {
  return useBlocCartes<TopCentresCartes>('centres', plage, active);
}

/** Commandes annulées par motif (parmi les demandes). */
export function useAnnulations(plage: Plage | undefined, active = true) {
  return useBlocCartes<AnnulationsParMotif>('annulations', plage, active);
}
