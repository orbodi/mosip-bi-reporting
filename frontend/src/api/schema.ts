/**
 * Types de l'API, générés par openapi-typescript depuis /v3/api-docs (npm run api:types, backend démarré).
 * Amorce écrite à la main pour /api/v1/meta, /api/v1/meta/regions et /api/v1/enrolement/* (devenir, semaines,
 * territoire, centres, preinscriptions, age-sexe) : la régénérer dès que le backend tourne.
 * Ne pas modifier à la main ensuite.
 */
export interface paths {
  '/api/v1/meta': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['Meta'];
          };
        };
      };
    };
  };
  '/api/v1/enrolement/devenir': {
    get: {
      parameters: {
        query?: {
          du?: string;
          au?: string;
          zone?: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['DevenirInscriptions'];
          };
        };
      };
    };
  };
  '/api/v1/meta/regions': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['Region'][];
          };
        };
      };
    };
  };
  '/api/v1/enrolement/semaines': {
    get: {
      parameters: {
        query?: {
          du?: string;
          au?: string;
          zone?: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['InscriptionsParSemaine'];
          };
        };
      };
    };
  };
  '/api/v1/enrolement/territoire': {
    get: {
      parameters: {
        query?: {
          du?: string;
          au?: string;
          zone?: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['Territoire'];
          };
        };
      };
    };
  };
  '/api/v1/enrolement/preinscriptions/profil': {
    get: {
      parameters: {
        query?: {
          du?: string;
          au?: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['ProfilPreinscriptions'];
          };
        };
      };
    };
  };
  '/api/v1/enrolement/preinscriptions': {
    get: {
      parameters: {
        query?: {
          du?: string;
          au?: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['Preinscriptions'];
          };
        };
      };
    };
  };
  '/api/v1/enrolement/age-sexe': {
    get: {
      parameters: {
        query?: {
          du?: string;
          au?: string;
          zone?: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['AgeSexe'];
          };
        };
      };
    };
  };
  '/api/v1/enrolement/centres': {
    get: {
      parameters: {
        query?: {
          du?: string;
          au?: string;
          zone?: string;
          classement?: 'inscriptions' | 'echecs' | 'rejets';
        };
      };
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['TopCentres'];
          };
        };
      };
    };
  };
}

export interface components {
  schemas: {
    Meta: {
      application: string;
      sources: components['schemas']['FraicheurSource'][];
    };
    FraicheurSource: {
      source: string;
      libelle: string;
      /** Format: date */
      premiereDonnee?: string | null;
      /** Format: date-time */
      derniereDonnee?: string | null;
      /** Format: date-time */
      dernierChargement?: string | null;
    };
    DevenirInscriptions: {
      perimetre: string;
      /** Format: date */
      du?: string | null;
      /** Format: date */
      au?: string | null;
      /** Format: int64 */
      inscriptions: number;
      /** Format: int64 */
      niuGeneres: number;
      /** Format: int64 */
      enCours: number;
      /** Format: int64 */
      echouees: number;
      /** Format: int64 */
      rejetees: number;
      /** Format: int64 */
      nonClassees: number;
    };
    Region: {
      code: string;
      nom: string;
    };
    InscriptionsParSemaine: {
      perimetre: string;
      /** Format: date */
      du?: string | null;
      /** Format: date */
      au?: string | null;
      niuDisponibles: boolean;
      semaines: components['schemas']['Semaine'][];
    };
    Semaine: {
      /** Format: date */
      lundi: string;
      dansLaPeriode: boolean;
      /** Format: int64 */
      inscriptions: number;
      /** Format: int64 */
      niuGeneres: number;
    };
    Territoire: {
      perimetre: string;
      zone?: string | null;
      niveau?: string | null;
      ascendants: components['schemas']['ZoneParente'][];
      /** Format: date */
      du?: string | null;
      /** Format: date */
      au?: string | null;
      /** Format: int64 */
      inscriptions: number;
      /** Format: int64 */
      niuGeneres: number;
      /** Format: int64 */
      enCours: number;
      /** Format: int64 */
      echouees: number;
      /** Format: int64 */
      rejetees: number;
      /** Format: int64 */
      nonClassees: number;
      /** Format: int64 */
      preinscriptions: number;
      /**
       * Format: int32
       * @description Délai médian de la réception au NIU (heures, premières inscriptions), null sans NIU
       */
      delaiMedianH?: number | null;
      lignes: components['schemas']['LigneZone'][];
    };
    LigneZone: {
      code: string;
      nom: string;
      niveau: string;
      horsReferentiel: boolean;
      /** Format: int64 */
      inscriptions: number;
      /** Format: int64 */
      niuGeneres: number;
      /** Format: int64 */
      enCours: number;
      /** Format: int64 */
      echouees: number;
      /** Format: int64 */
      rejetees: number;
      /** Format: int64 */
      nonClassees: number;
      /** Format: int64 */
      preinscriptions: number;
      /**
       * Format: int32
       * @description Délai médian de la réception au NIU (heures, premières inscriptions), null sans NIU
       */
      delaiMedianH?: number | null;
      ouvrable: boolean;
    };
    ZoneParente: {
      code: string;
      nom: string;
      niveau: string;
    };
    TopCentres: {
      perimetre: string;
      classement: string;
      centres: components['schemas']['CentreClasse'][];
    };
    Preinscriptions: {
      perimetre: string;
      /** Format: date */
      du?: string | null;
      /** Format: date */
      au?: string | null;
      disponible: boolean;
      /** Format: int64 */
      demandes?: number | null;
      /** Format: int64 */
      rendezVousReserves?: number | null;
      /** Format: int64 */
      enAttenteRendezVous?: number | null;
      /** Format: int64 */
      expirees?: number | null;
      /** Format: int64 */
      annulees?: number | null;
      /** Format: int64 */
      honorees?: number | null;
      /** Format: int64 */
      nonClassees?: number | null;
      /** Format: int64 */
      femmes?: number | null;
      /** Format: int64 */
      hommes?: number | null;
      /** Format: date-time */
      derniereDemande?: string | null;
    };
    AgeSexe: {
      perimetre: string;
      /** Format: date */
      du?: string | null;
      /** Format: date */
      au?: string | null;
      disponible: boolean;
      tranches: components['schemas']['Tranche'][];
      /** Format: int64 */
      nonRenseignes?: number | null;
    };
    ProfilPreinscriptions: {
      perimetre: string;
      /** Format: date */
      du?: string | null;
      /** Format: date */
      au?: string | null;
      disponible: boolean;
      tranches: components['schemas']['Tranche'][];
      /** Format: int64 */
      nonRenseignes?: number | null;
      nationalites: components['schemas']['Nationalite'][];
    };
    Nationalite: {
      nom: string;
      /** Format: int64 */
      demandes: number;
    };
    Tranche: {
      tranche: string;
      /** Format: int64 */
      femmes?: number | null;
      /** Format: int64 */
      hommes?: number | null;
    };
    CentreClasse: {
      /** Format: int32 */
      rang: number;
      code: string;
      nom: string;
      prefecture?: string | null;
      region?: string | null;
      /** Format: int64 */
      valeur: number;
      /** Format: int64 */
      inscriptions: number;
    };
  };
}
