import { keepPreviousData, useQuery } from '@tanstack/react-query';
import type { Plage } from '../lib/periode';
import {
  RAFRAICHISSEMENT_MS,
  lireApi,
  type AgeSexe,
  type ArretsParEtape,
  type DelaisTraitement,
  type DevenirInscriptions,
  type Preinscriptions,
  type ProfilPreinscriptions,
  type InscriptionsParSemaine,
  type PaquetsEnCours,
  type SynchronisationNonRecue,
  type Territoire,
  type TopCentres,
} from './client';

/** Classements du bloc « Top des centres » (paramètre classement de l'API). */
export type ClassementCentres = 'inscriptions' | 'echecs' | 'rejets' | 'remontee';

/**
 * Lecture d'un bloc de la page Enrôlement, relue toutes les 30 s comme le pipeline temps réel. Sans plage, l'API
 * prend toutes les données disponibles ; sans zone, tout le Togo.
 */
function useBlocEnrolement<T>(
  ressource: string,
  plage: Plage | undefined,
  active: boolean,
  autres: Record<string, string | undefined> = {},
) {
  const parametres = { du: plage?.du, au: plage?.au, ...autres };
  return useQuery({
    queryKey: ['enrolement', ressource, parametres],
    queryFn: () => lireApi<T>(`/enrolement/${ressource}`, parametres),
    enabled: active,
    refetchInterval: RAFRAICHISSEMENT_MS,
    // Pas de clignotement quand un filtre change : les anciens chiffres restent affichés pendant le chargement.
    placeholderData: keepPreviousData,
  });
}

/** Devenir des inscriptions (GET /api/v1/enrolement/devenir). */
export function useDevenirInscriptions(plage: Plage | undefined, active = true) {
  return useQuery({
    queryKey: ['enrolement', 'devenir', plage?.du ?? null, plage?.au ?? null],
    queryFn: () => lireApi<DevenirInscriptions>('/enrolement/devenir', { du: plage?.du, au: plage?.au }),
    enabled: active,
    refetchInterval: RAFRAICHISSEMENT_MS,
    placeholderData: keepPreviousData,
  });
}

/** Inscriptions et NIU des 12 semaines complètes (GET /api/v1/enrolement/semaines). */
export function useSemaines(plage: Plage | undefined, active = true) {
  return useBlocEnrolement<InscriptionsParSemaine>('semaines', plage, active);
}

/** Territoire : totaux de la zone et ses sous-zones (GET /api/v1/enrolement/territoire). */
export function useTerritoire(plage: Plage | undefined, zone: string | undefined, active = true) {
  return useBlocEnrolement<Territoire>('territoire', plage, active, { zone });
}

/** Top des centres (GET /api/v1/enrolement/centres). */
export function useTopCentres(
  plage: Plage | undefined,
  zone: string | undefined,
  classement: ClassementCentres,
  active = true,
) {
  return useBlocEnrolement<TopCentres>('centres', plage, active, { zone, classement });
}

/** Pré-inscriptions, nationales (GET /api/v1/enrolement/preinscriptions). */
export function usePreinscriptions(plage: Plage | undefined, active = true) {
  return useBlocEnrolement<Preinscriptions>('preinscriptions', plage, active);
}

/** Profil des pré-inscrits : âge et sexe, nationalité ; national (GET /api/v1/enrolement/preinscriptions/profil). */
export function useProfilPreinscriptions(plage: Plage | undefined, active = true) {
  return useBlocEnrolement<ProfilPreinscriptions>('preinscriptions/profil', plage, active);
}

/** NIU générés par sexe et tranche d'âge, Togo ou une région (GET /api/v1/enrolement/age-sexe). */
export function useAgeSexe(plage: Plage | undefined, zone: string | undefined, active = true) {
  return useBlocEnrolement<AgeSexe>('age-sexe', plage, active, { zone });
}

/** Où s'arrêtent les paquets : rejets et échecs par étape d'arrêt ; national (GET /api/v1/enrolement/etapes). */
export function useEtapes(plage: Plage | undefined, active = true) {
  return useBlocEnrolement<ArretsParEtape>('etapes', plage, active);
}

/** Paquets en cours par étape, dont bloqués ; stock sans période, national (GET /api/v1/enrolement/en-cours). */
export function useEnCours() {
  return useBlocEnrolement<PaquetsEnCours>('en-cours', undefined, true);
}

/** Délais de traitement en heures ; national (GET /api/v1/enrolement/delais). */
export function useDelais(plage: Plage | undefined, active = true) {
  return useBlocEnrolement<DelaisTraitement>('delais', plage, active);
}

/** Paquets synchronisés pas encore reçus ; stock, national (GET /api/v1/enrolement/synchronisation). */
export function useSynchronisation() {
  return useBlocEnrolement<SynchronisationNonRecue>('synchronisation', undefined, true);
}
