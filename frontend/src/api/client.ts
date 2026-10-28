import type { components } from './schema';

export type Meta = components['schemas']['Meta'];
export type FraicheurSource = components['schemas']['FraicheurSource'];
export type DevenirInscriptions = components['schemas']['DevenirInscriptions'];
export type Region = components['schemas']['Region'];
export type InscriptionsParSemaine = components['schemas']['InscriptionsParSemaine'];
export type Semaine = components['schemas']['Semaine'];
export type Territoire = components['schemas']['Territoire'];
export type LigneZone = components['schemas']['LigneZone'];
export type ZoneParente = components['schemas']['ZoneParente'];
export type TopCentres = components['schemas']['TopCentres'];
export type CentreClasse = components['schemas']['CentreClasse'];
export type Preinscriptions = components['schemas']['Preinscriptions'];
export type AgeSexe = components['schemas']['AgeSexe'];
export type TrancheAgeSexe = components['schemas']['Tranche'];
export type ProfilPreinscriptions = components['schemas']['ProfilPreinscriptions'];
export type NationalitePreinscription = components['schemas']['Nationalite'];
export type ArretsParEtape = components['schemas']['ArretsParEtape'];
export type MotifsArret = components['schemas']['MotifsArret'];
export type LigneMotif = components['schemas']['LigneMotif'];
export type EtapeArret = components['schemas']['EtapeArret'];
export type PaquetsEnCours = components['schemas']['PaquetsEnCours'];
export type EtapeEnCours = components['schemas']['EtapeEnCours'];
export type DelaisTraitement = components['schemas']['DelaisTraitement'];
export type MesureDelai = components['schemas']['Mesure'];
export type SynchronisationNonRecue = components['schemas']['SynchronisationNonRecue'];

/**
 * Relecture automatique des données alimentées en temps réel (pipeline CDC de l'enrôlement) : de l'ordre de la
 * minute entre MOSIP et l'écran avec le lot Spark de 10 s. Suspendue quand l'onglet n'est pas visible.
 */
export const RAFRAICHISSEMENT_MS = 30_000;

/** Base de l'API : même origine par défaut (proxy Vite en développement, reverse proxy en production). */
const BASE = import.meta.env.VITE_API_URL ?? '';

let fournisseurJeton: () => string | undefined = () => undefined;

/** Branché par l'authentification Keycloak pour joindre le jeton d'accès à chaque appel. */
export function definirFournisseurJeton(fournisseur: () => string | undefined) {
  fournisseurJeton = fournisseur;
}

export class ErreurApi extends Error {
  constructor(
    readonly statut: number,
    message: string,
  ) {
    super(message);
    this.name = 'ErreurApi';
  }
}

/** GET sur /api/v1{chemin} ; les paramètres vides sont omis. */
export async function lireApi<T>(
  chemin: string,
  parametres: Record<string, string | undefined> = {},
): Promise<T> {
  const url = new URL(`${BASE}/api/v1${chemin}`, window.location.origin);
  for (const [cle, valeur] of Object.entries(parametres)) {
    if (valeur) url.searchParams.set(cle, valeur);
  }
  const jeton = fournisseurJeton();
  const reponse = await fetch(url, {
    headers: { Accept: 'application/json', ...(jeton ? { Authorization: `Bearer ${jeton}` } : {}) },
  });
  if (!reponse.ok) {
    throw new ErreurApi(reponse.status, `Appel ${chemin} : statut ${reponse.status}`);
  }
  return (await reponse.json()) as T;
}
