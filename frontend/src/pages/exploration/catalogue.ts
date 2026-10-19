import type { CodeSource } from '../../api/meta';

/** Dimensions de ventilation de l'Exploration (maquette/pages/Technique.dc.html). */
export type CleDimension = 'sexe' | 'age' | 'type' | 'taut' | 'cause' | 'part' | 'terr';

export interface Indicateur {
  cle: string;
  libelle: string;
  dimensions: CleDimension[];
  /** Ventilable par territoire (région, préfecture…). */
  territoire: boolean;
}

export interface SourceExploration {
  cle: 'enrol' | 'cartes' | 'abis' | 'idps' | 'auth';
  libelle: string;
  /** Source de fraîcheur (bornes de la période). */
  fraicheur: CodeSource;
  note?: string;
  indicateurs: Indicateur[];
}

const PROFIL: CleDimension[] = ['sexe', 'age'];

export const SOURCES: SourceExploration[] = [
  {
    cle: 'enrol',
    libelle: 'Enrôlement',
    fraicheur: 'enrolement',
    indicateurs: [
      { cle: 'ins', libelle: 'Inscriptions', dimensions: [...PROFIL, 'type'], territoire: true },
      { cle: 'niu', libelle: 'NIU générés', dimensions: PROFIL, territoire: true },
      { cle: 'enc', libelle: 'Inscriptions en cours', dimensions: PROFIL, territoire: true },
      { cle: 'ech', libelle: 'Inscriptions échouées', dimensions: PROFIL, territoire: true },
      { cle: 'rej', libelle: 'Inscriptions rejetées', dimensions: PROFIL, territoire: true },
    ],
  },
  {
    cle: 'cartes',
    libelle: 'Impression des cartes',
    fraicheur: 'cartes',
    indicateurs: [
      { cle: 'dem', libelle: 'Demandes d’impression', dimensions: PROFIL, territoire: true },
      { cle: 'exp', libelle: 'Cartes imprimées et expédiées', dimensions: PROFIL, territoire: true },
      { cle: 'rem', libelle: 'Cartes remises', dimensions: PROFIL, territoire: true },
      { cle: 'arem', libelle: 'Cartes à remettre', dimensions: PROFIL, territoire: true },
    ],
  },
  {
    cle: 'abis',
    libelle: 'ABIS',
    fraicheur: 'abis',
    note: 'Les journaux ABIS ne contiennent ni région ni profil du citoyen : seules les ventilations par date sont disponibles.',
    indicateurs: [
      { cle: 'ins', libelle: 'Requêtes d’insertion', dimensions: [], territoire: false },
      { cle: 'dedup', libelle: 'Requêtes de déduplication', dimensions: [], territoire: false },
      { cle: 'adj', libelle: 'Requêtes d’adjudication', dimensions: [], territoire: false },
      { cle: 'trt', libelle: 'Cas d’adjudication traités', dimensions: [], territoire: false },
      { cle: 'hit', libelle: 'Dossiers HIT', dimensions: [], territoire: false },
      { cle: 'nohit', libelle: 'Dossiers NO HIT', dimensions: [], territoire: false },
      { cle: 'eins', libelle: 'Erreurs d’insertion', dimensions: [], territoire: false },
      { cle: 'eid', libelle: 'Erreurs d’identification', dimensions: [], territoire: false },
      { cle: 'eadj', libelle: 'Erreurs d’adjudication', dimensions: [], territoire: false },
    ],
  },
  {
    cle: 'idps',
    libelle: 'IDPS',
    fraicheur: 'idps',
    note: 'Le circuit IDPS est en pilote : seules les régions pilotes ont des ordres.',
    indicateurs: [
      { cle: 'ord', libelle: 'Ordres d’impression reçus', dimensions: [], territoire: true },
      { cle: 'att', libelle: 'Ordres en attente', dimensions: [], territoire: true },
      { cle: 'err', libelle: 'Erreurs d’impression', dimensions: ['terr'], territoire: true },
    ],
  },
  {
    cle: 'auth',
    libelle: 'Authentifications',
    fraicheur: 'authentifications',
    note: 'Les requêtes d’authentification ne portent pas la région du demandeur.',
    indicateurs: [
      { cle: 'req', libelle: 'Requêtes', dimensions: ['taut', 'part'], territoire: false },
      { cle: 'ok', libelle: 'Requêtes réussies', dimensions: ['taut', 'part'], territoire: false },
      { cle: 'ko', libelle: 'Requêtes échouées', dimensions: ['taut', 'cause', 'part'], territoire: false },
    ],
  },
];

export const DIMENSIONS: Record<CleDimension, { libelle: string; tous: string; valeurs: string[] }> = {
  sexe: { libelle: 'Sexe', tous: 'Tous', valeurs: ['Femmes', 'Hommes'] },
  age: {
    libelle: 'Tranche d’âge',
    tous: 'Toutes',
    valeurs: [
      '0 à 5 ans',
      '6 à 14 ans',
      '15 à 18 ans',
      '19 à 25 ans',
      '26 à 35 ans',
      '36 à 45 ans',
      '46 à 60 ans',
      '60 ans et +',
    ],
  },
  type: {
    libelle: 'Type de demande',
    tous: 'Tous',
    valeurs: [
      'Nouvelle inscription',
      'Mise à jour',
      'Mise à jour par le citoyen',
      'Correction',
      'Réimpression de carte',
      'Récupération de NIU',
      'Activation',
      'Désactivation',
    ],
  },
  taut: {
    libelle: 'Type d’authentification',
    tous: 'Tous',
    valeurs: ['Biométrique', 'Code à usage unique', 'Démographique', 'Combinée'],
  },
  cause: { libelle: 'Cause d’échec', tous: 'Toutes', valeurs: [] },
  part: { libelle: 'Partenaire', tous: 'Tous', valeurs: [] },
  terr: {
    libelle: 'Type d’erreur',
    tous: 'Tous',
    valeurs: ['Personnalisation', 'Contrôle qualité', 'Supervision'],
  },
};

export const NIVEAUX_TERRITOIRE = [
  { cle: 'region', libelle: 'Région' },
  { cle: 'pref', libelle: 'Préfecture' },
  { cle: 'commune', libelle: 'Commune' },
  { cle: 'canton', libelle: 'Canton' },
  { cle: 'localite', libelle: 'Localité' },
  { cle: 'centre', libelle: 'Centre' },
] as const;

/** Nombre total d'indicateurs (24) affiché dans l'introduction. */
export const NOMBRE_INDICATEURS = SOURCES.reduce((t, s) => t + s.indicateurs.length, 0);
