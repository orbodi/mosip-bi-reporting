import { keepPreviousData, useQuery } from '@tanstack/react-query';
import type { Plage } from '../lib/periode';
import {
  RAFRAICHISSEMENT_MS,
  lireApi,
  type AuthentificationsParSemaine,
  type CausesEchec,
  type ExplorationAuthentifications,
  type PartenairesEtCanaux,
  type RequetesUsagers,
  type TypesAuthentification,
  type VerificationsPaquets,
} from './client';

/**
 * Lecture d'un bloc de la page Authentifications (GET /api/v1/authentifications/…), relue comme les autres pages : le
 * pipeline publie toutes les 5 minutes. Sans plage, l'API prend toutes les données. Pas de zone : une authentification
 * n'a pas de territoire.
 */
function useBlocAuthentifications<T>(
  ressource: string,
  plage: Plage | undefined,
  active: boolean,
  autres: Record<string, string | undefined> = {},
) {
  const parametres = { du: plage?.du, au: plage?.au, ...autres };
  return useQuery({
    queryKey: ['authentifications', ressource, parametres],
    queryFn: () => lireApi<T>(`/authentifications/${ressource}`, parametres),
    enabled: active,
    refetchInterval: RAFRAICHISSEMENT_MS,
    placeholderData: keepPreviousData,
  });
}

/** Requêtes des usagers : statut, type, partenaires raccordés, demandes et codes OTP. */
export function useUsagers(plage: Plage | undefined, active = true) {
  return useBlocAuthentifications<RequetesUsagers>('usagers', plage, active);
}

/** Requêtes et échecs des usagers par type d'authentification. */
export function useTypesAuthentification(plage: Plage | undefined, active = true) {
  return useBlocAuthentifications<TypesAuthentification>('types', plage, active);
}

/** Causes des échecs des usagers ou du traitement des paquets. */
export function useCausesEchec(perimetre: 'usagers' | 'paquets', plage: Plage | undefined, active = true) {
  return useBlocAuthentifications<CausesEchec>('causes', plage, active, { perimetre });
}

/** Partenaires et canaux des usagers, du plus actif au moins actif. */
export function usePartenaires(plage: Plage | undefined, active = true) {
  return useBlocAuthentifications<PartenairesEtCanaux>('partenaires', plage, active);
}

/** Requêtes réussies et échouées des usagers des 12 semaines complètes. */
export function useSemainesAuthentification(plage: Plage | undefined, active = true) {
  return useBlocAuthentifications<AuthentificationsParSemaine>('semaines', plage, active);
}

/** Vérifications biométriques du traitement des paquets (bloc à part). */
export function usePaquets(plage: Plage | undefined, active = true) {
  return useBlocAuthentifications<VerificationsPaquets>('paquets', plage, active);
}

/** Paramètres de l'onglet Authentifications de l'Exploration (filtres facultatifs, une ventilation). */
export interface ParametresExploration {
  perimetre: 'usagers' | 'paquets';
  type?: string;
  motif?: string;
  appelant?: string;
  par: 'annee' | 'mois' | 'type' | 'motif' | 'appelant' | 'total';
}

/** Onglet Authentifications de l'Exploration : lignes de la ventilation, total et valeurs des filtres. */
export function useExplorationAuthentifications(
  plage: Plage | undefined,
  parametres: ParametresExploration,
  active = true,
) {
  return useBlocAuthentifications<ExplorationAuthentifications>('exploration', plage, active, { ...parametres });
}
