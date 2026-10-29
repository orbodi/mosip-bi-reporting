/**
 * Types de l'API, générés par openapi-typescript depuis /v3/api-docs (npm run api:types, backend démarré).
 * Amorce écrite à la main pour /api/v1/meta, /api/v1/meta/regions et /api/v1/enrolement/* (devenir, semaines,
 * territoire, centres, preinscriptions, age-sexe, etapes, motifs, en-cours, delais, synchronisation) : la régénérer dès
 * que le backend tourne.
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
  '/api/v1/enrolement/jours': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['InscriptionsParJour'];
          };
        };
      };
    };
  };
  '/api/v1/enrolement/suivi': {
    post: {
      requestBody: {
        content: {
          'application/json': components['schemas']['DemandeSuivi'];
        };
      };
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['SuiviDossier'];
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
          classement?: 'inscriptions' | 'echecs' | 'rejets' | 'remontee';
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
  '/api/v1/enrolement/etapes': {
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
            'application/json': components['schemas']['ArretsParEtape'];
          };
        };
      };
    };
  };
  '/api/v1/enrolement/motifs': {
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
            'application/json': components['schemas']['MotifsArret'];
          };
        };
      };
    };
  };
  '/api/v1/enrolement/en-cours': {
    get: {
      parameters: {
        query?: {
          zone?: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['PaquetsEnCours'];
          };
        };
      };
    };
  };
  '/api/v1/enrolement/delais': {
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
            'application/json': components['schemas']['DelaisTraitement'];
          };
        };
      };
    };
  };
  '/api/v1/enrolement/synchronisation': {
    get: {
      parameters: {
        query?: {
          zone?: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': components['schemas']['SynchronisationNonRecue'];
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
      /**
       * Format: int64
       * @description Dont en cours depuis plus de 30 jours (stock), null quand une période est demandée
       */
      bloques?: number | null;
    };
    Region: {
      code: string;
      nom: string;
    };
    DemandeSuivi: {
      /** @description Numéro d'inscription, 29 chiffres */
      rid?: string;
    };
    SuiviDossier: {
      typeDemande: string;
      /** @description niu, en_cours, echoue, rejete, non_classe ou non_recu */
      devenir: string;
      bloque: boolean;
      centre: components['schemas']['Centre'];
      etape?: components['schemas']['EtapeSuivi'] | null;
      motif?: components['schemas']['MotifSuivi'] | null;
      /** Format: date-time */
      derniereActiviteLe?: string | null;
      jalons: components['schemas']['Jalons'];
      /** Format: date-time */
      majLe: string;
    };
    Centre: {
      nom: string;
      prefecture?: string | null;
      region?: string | null;
    };
    EtapeSuivi: {
      code: string;
      libelle: string;
      statut?: string | null;
    };
    MotifSuivi: {
      code: string;
      libelle: string;
      commentaire?: string | null;
    };
    Jalons: {
      /** Format: date-time */
      enroleLe?: string | null;
      /** Format: date-time */
      synchroniseLe?: string | null;
      refusPoste: boolean;
      /** Format: date-time */
      recuLe?: string | null;
      /** Format: date-time */
      niuLe?: string | null;
    };
    InscriptionsParJour: {
      perimetre: string;
      /** Format: date */
      aujourdhui: string;
      niuDisponibles: boolean;
      jours: components['schemas']['JourInscriptions'][];
    };
    JourInscriptions: {
      /** Format: date */
      jour: string;
      /** Format: int64 */
      inscriptions: number;
      /** Format: int64 */
      niuGeneres: number;
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
    ArretsParEtape: {
      perimetre: string;
      /** Format: date */
      du?: string | null;
      /** Format: date */
      au?: string | null;
      /** Format: int64 */
      totalRejets: number;
      /** Format: int64 */
      totalEchecs: number;
      rejets: components['schemas']['EtapeArret'][];
      echecs: components['schemas']['EtapeArret'][];
    };
    EtapeArret: {
      /** @description Code MOSIP de l'étape (ou REFUS_POSTE), null pour « Autres étapes » */
      code?: string | null;
      libelle: string;
      /** Format: int64 */
      inscriptions: number;
    };
    MotifsArret: {
      perimetre: string;
      /** Format: date */
      du?: string | null;
      /** Format: date */
      au?: string | null;
      /** Format: date-time */
      calculeLe?: string | null;
      /** Format: int32 */
      seuilJours: number;
      /** Format: int64 */
      totalRejets: number;
      /** Format: int64 */
      totalEchecs: number;
      /** Format: int64 */
      totalEnCours: number;
      /** Format: int64 */
      bloques: number;
      rejets: components['schemas']['LigneMotif'][];
      echecs: components['schemas']['LigneMotif'][];
      enCours: components['schemas']['LigneMotif'][];
    };
    LigneMotif: {
      /** @description Code du motif (REFUS_SUPERVISEUR…), null pour « Autres cas » */
      motif?: string | null;
      libelle: string;
      /** @description Message type de MOSIP pour ce motif (catalogue), null si aucun */
      commentaire?: string | null;
      /** @description Ce qu'il faut vérifier pour ce motif (catalogue), null pour « Autres cas » */
      piste?: string | null;
      /** @description Étape principale de MOSIP (reg_stage_name), celle qui compte le plus de paquets pour ce motif ; null pour « Autres cas » */
      stage?: string | null;
      stageLibelle?: string | null;
      /**
       * Format: int32
       * @description Nombre d'autres étapes où MOSIP pose ce motif (0 si une seule, et pour « Autres cas »)
       */
      autresEtapes: number;
      /** Format: int64 */
      inscriptions: number;
      /** Format: int64 */
      bloques: number;
    };
    PaquetsEnCours: {
      perimetre: string;
      /** Format: date-time */
      calculeLe?: string | null;
      /** Format: int32 */
      seuilJours: number;
      /** Format: int64 */
      total: number;
      /** Format: int64 */
      bloques: number;
      etapes: components['schemas']['EtapeEnCours'][];
    };
    EtapeEnCours: {
      code?: string | null;
      libelle: string;
      /** Format: int64 */
      inscriptions: number;
      /** Format: int64 */
      bloques: number;
    };
    DelaisTraitement: {
      perimetre: string;
      /** Format: date */
      du?: string | null;
      /** Format: date */
      au?: string | null;
      receptionNiu: components['schemas']['Mesure'];
      enrolementReception: components['schemas']['Mesure'];
    };
    Mesure: {
      /** Format: int64 */
      paquets: number;
      /**
       * Format: int32
       * @description Borne basse de la classe de la médiane, en heures ; null sans paquet
       */
      medianeH?: number | null;
      /**
       * Format: int32
       * @description Borne basse de la classe du 90e centile, en heures ; null sans paquet
       */
      centile90H?: number | null;
      /** Format: int64 */
      moins24h: number;
    };
    SynchronisationNonRecue: {
      perimetre: string;
      /** Format: date-time */
      calculeLe?: string | null;
      /** Format: int64 */
      nonRecus: number;
      /** Format: int64 */
      plusDe7Jours: number;
      /** Format: date-time */
      plusAncienneLe?: string | null;
    };
  };
}
