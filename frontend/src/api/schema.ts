/**
 * Types de l'API, générés par openapi-typescript depuis /v3/api-docs (npm run api:types, backend démarré).
 * Amorce écrite à la main pour /api/v1/meta et /api/v1/enrolement/devenir : la régénérer dès que le backend tourne.
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
  };
}
