/**
 * Types de l'API, générés par openapi-typescript depuis /v3/api-docs (npm run api:types, backend démarré).
 * Amorce écrite à la main pour /api/v1/meta, /api/v1/meta/regions et /api/v1/enrolement/* (devenir, semaines,
 * territoire, centres) : la régénérer dès que le backend tourne.
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
    };
    TopCentres: {
      perimetre: string;
      classement: string;
      centres: components['schemas']['CentreClasse'][];
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
