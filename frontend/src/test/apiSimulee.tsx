import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createMemoryHistory } from '@tanstack/react-router';
import { render } from '@testing-library/react';
import { vi } from 'vitest';
import type {
  AgeSexe,
  DelaisTraitement,
  InscriptionsParJour,
  InscriptionsParSemaine,
  LigneZone,
  MotifsArret,
  Preinscriptions,
  ProfilPreinscriptions,
  Region,
  SuiviDossier,
  SynchronisationNonRecue,
  Territoire,
  TopCentres,
} from '../api/client';
import { creerRouteur } from '../routeur';

/** Réponses de l'API pour les tests des pages (chiffres de la maquette Enrôlement, dernière donnée le 14/01/2026). */
export const META = {
  application: 'BI Reporting ANID',
  sources: [
    {
      source: 'enrolement',
      libelle: 'Enrôlement',
      premiereDonnee: '2024-01-01',
      derniereDonnee: '2026-01-14T11:42:00Z',
      dernierChargement: '2026-01-14T11:45:00Z',
    },
    {
      source: 'preinscription',
      libelle: 'Pré-inscription',
      premiereDonnee: '2024-01-01',
      derniereDonnee: '2026-01-14T11:28:00Z',
      dernierChargement: '2026-01-14T11:50:00Z',
    },
  ],
};

export const REGIONS: Region[] = [
  { code: 'SAV', nom: 'Savanes' },
  { code: 'KAR', nom: 'Kara' },
  { code: 'CEN', nom: 'Centrale' },
  { code: 'PLA', nom: 'Plateaux' },
  { code: 'MAR', nom: 'Maritime' },
  { code: 'GLO', nom: 'Grand Lomé' },
];

const zone = (
  code: string,
  nom: string,
  niveau: string,
  ins: number,
  niu: number,
  rej: number,
): LigneZone => ({
  code,
  nom,
  niveau,
  horsReferentiel: false,
  inscriptions: ins,
  niuGeneres: niu,
  rejetees: rej,
  echouees: Math.round(ins * 0.003),
  enCours: ins - niu - rej - Math.round(ins * 0.003),
  nonClassees: 0,
  preinscriptions: Math.round(ins * 0.4),
  ouvrable: niveau !== 'centre',
});

const totaux = (lignes: LigneZone[]) => ({
  inscriptions: lignes.reduce((s, l) => s + l.inscriptions, 0),
  niuGeneres: lignes.reduce((s, l) => s + l.niuGeneres, 0),
  enCours: lignes.reduce((s, l) => s + l.enCours, 0),
  echouees: lignes.reduce((s, l) => s + l.echouees, 0),
  rejetees: lignes.reduce((s, l) => s + l.rejetees, 0),
  nonClassees: 0,
  preinscriptions: lignes.reduce((s, l) => s + l.preinscriptions, 0),
});

const LIGNES_REGIONS = [
  zone('SAV', 'Savanes', 'region', 450239, 413573, 16072),
  zone('KAR', 'Kara', 'region', 386000, 358514, 11069),
  zone('CEN', 'Centrale', 'region', 312000, 288857, 9516),
  zone('PLA', 'Plateaux', 'region', 598000, 556639, 16541),
  zone('MAR', 'Maritime', 'region', 512000, 479495, 12381),
  zone('GLO', 'Grand Lomé', 'region', 1020000, 961808, 20917),
];

export const TERRITOIRE_NATIONAL: Territoire = {
  perimetre: 'Ensemble du Togo',
  zone: null,
  niveau: null,
  ascendants: [],
  ...totaux(LIGNES_REGIONS),
  lignes: LIGNES_REGIONS,
};

const LIGNES_SAVANES = [
  zone('SAV-01', 'Cinkassé', 'prefecture', 74000, 67500, 2812),
  zone('SAV-02', 'Tône', 'prefecture', 186239, 171000, 6332),
  zone('SAV-03', 'Kpendjal', 'prefecture', 62000, 56300, 2542),
  zone('SAV-04', 'Tandjouaré', 'prefecture', 56000, 51400, 2016),
  zone('SAV-05', 'Oti', 'prefecture', 72000, 65800, 2664),
];

export const TERRITOIRE_SAVANES: Territoire = {
  perimetre: 'Savanes',
  zone: 'SAV',
  niveau: 'region',
  ascendants: [],
  ...totaux(LIGNES_SAVANES),
  lignes: LIGNES_SAVANES,
};

// Tône : communes, dont une sans inscription (masquée) ; pré-inscriptions nulles sous la préfecture.
const LIGNES_TONE = [
  { ...zone('SAV-02-C1', 'Tône 1', 'commune', 66239, 61000, 2300), preinscriptions: 0 },
  { ...zone('SAV-02-C2', 'Tône 2', 'commune', 120000, 110000, 4032), preinscriptions: 0 },
  { ...zone('SAV-02-C3', 'Tône 3', 'commune', 0, 0, 0), preinscriptions: 0 },
];

export const TERRITOIRE_TONE: Territoire = {
  perimetre: 'Tône',
  zone: 'SAV-02',
  niveau: 'prefecture',
  ascendants: [{ code: 'SAV', nom: 'Savanes', niveau: 'region' }],
  ...totaux(LIGNES_TONE),
  lignes: LIGNES_TONE,
};

// Un canton dont un centre est rattaché directement (cas réel), à côté d'une localité.
const LIGNES_CANTON = [
  { ...zone('SAV-02-L1', 'Nano', 'localite', 1200, 1100, 30), preinscriptions: 0 },
  { ...zone('10092', 'EPP Nano', 'centre', 300, 280, 5), preinscriptions: 0 },
];

export const TERRITOIRE_CANTON: Territoire = {
  perimetre: 'Canton de Nano',
  zone: 'SAV-02-K1',
  niveau: 'canton',
  ascendants: [
    { code: 'SAV', nom: 'Savanes', niveau: 'region' },
    { code: 'SAV-02', nom: 'Tône', niveau: 'prefecture' },
    { code: 'SAV-02-C2', nom: 'Tône 2', niveau: 'commune' },
  ],
  ...totaux(LIGNES_CANTON),
  lignes: LIGNES_CANTON,
};

// Un canton de 25 localités (pagination : 20 par page par défaut), inscriptions décroissantes de 2 500 à 100.
const LIGNES_CANTON_LONG = Array.from({ length: 25 }, (_, i) => ({
  ...zone(
    `SAV-02-L${100 + i}`,
    `Localité ${String(i + 1).padStart(2, '0')}`,
    'localite',
    2500 - i * 100,
    2000 - i * 80,
    10,
  ),
  preinscriptions: 0,
}));

export const TERRITOIRE_CANTON_LONG: Territoire = {
  perimetre: 'Canton de Dapaong',
  zone: 'SAV-02-K2',
  niveau: 'canton',
  ascendants: [
    { code: 'SAV', nom: 'Savanes', niveau: 'region' },
    { code: 'SAV-02', nom: 'Tône', niveau: 'prefecture' },
    { code: 'SAV-02-C2', nom: 'Tône 2', niveau: 'commune' },
  ],
  ...totaux(LIGNES_CANTON_LONG),
  lignes: LIGNES_CANTON_LONG,
};

const TERRITOIRES: Record<string, Territoire> = {
  SAV: TERRITOIRE_SAVANES,
  'SAV-02-K2': TERRITOIRE_CANTON_LONG,
  'SAV-02': TERRITOIRE_TONE,
  'SAV-02-K1': TERRITOIRE_CANTON,
};

const LUNDIS = [
  '2025-10-20',
  '2025-10-27',
  '2025-11-03',
  '2025-11-10',
  '2025-11-17',
  '2025-11-24',
  '2025-12-01',
  '2025-12-08',
  '2025-12-15',
  '2025-12-22',
  '2025-12-29',
  '2026-01-05',
];

export const SEMAINES: InscriptionsParSemaine = {
  perimetre: 'Ensemble du Togo',
  niuDisponibles: true,
  semaines: LUNDIS.map((lundi, i) => ({
    lundi,
    dansLaPeriode: true,
    inscriptions: i === 11 ? 20230 : 30000 + i * 500,
    niuGeneres: i === 11 ? 17626 : 28000 + i * 400,
  })),
};

/**
 * 28 jours jusqu'au mercredi 14/01/2026 (« aujourd'hui » des tests) : du 18/12/2025 au 14/01/2026. Inscriptions
 * 4 000 + 10 × rang, NIU 2 500 + 10 × rang ; le 14/01 (jour en cours) : 2 134 inscriptions, 1 388 NIU.
 */
export const JOURS: InscriptionsParJour = {
  perimetre: 'Ensemble du Togo',
  aujourdhui: '2026-01-14',
  niuDisponibles: true,
  jours: Array.from({ length: 28 }, (_, i) => {
    const d = new Date(Date.UTC(2025, 11, 18 + i));
    const dernier = i === 27;
    return {
      jour: d.toISOString().slice(0, 10),
      inscriptions: dernier ? 2134 : 4000 + 10 * i,
      niuGeneres: dernier ? 1388 : 2500 + 10 * i,
    };
  }),
};

/** RID d'essai du suivi d'un dossier (fictif) : seul celui-ci est « connu » de l'API simulée. */
export const RID_CONNU = '20101100230041220261021093015';

/** Dossier en cours, arrêté en vérification manuelle depuis le 18/09/2026 (bloqué). */
export const SUIVI: SuiviDossier = {
  typeDemande: 'NEW',
  devenir: 'en_cours',
  bloque: true,
  centre: { nom: 'EPP Doumassesse I G/B', prefecture: 'Golfe', region: 'Grand Lomé' },
  etape: { code: 'MANUAL_VERIFICATION', libelle: 'Vérification manuelle', statut: 'IN_PROGRESS' },
  motif: {
    code: 'FILE_VERIF_MANUELLE',
    libelle: 'En file d’attente de vérification manuelle',
    commentaire: 'Manual verification Sent to queue',
  },
  derniereActiviteLe: '2026-09-18T09:00:00Z',
  jalons: {
    enroleLe: '2026-09-02T10:14:00Z',
    synchroniseLe: '2026-09-02T17:40:00Z',
    refusPoste: false,
    recuLe: '2026-09-03T08:05:00Z',
    niuLe: null,
  },
  majLe: '2026-10-29T07:30:00Z',
};

export const CENTRES: Record<string, TopCentres> = {
  inscriptions: {
    perimetre: 'Ensemble du Togo',
    classement: 'inscriptions',
    centres: [
      {
        rang: 1,
        code: '20001',
        nom: 'EPP Doumassesse I G/B',
        prefecture: 'Golfe',
        region: 'Grand Lomé',
        valeur: 43534,
        inscriptions: 43534,
      },
      {
        rang: 2,
        code: '20002',
        nom: 'CEG Baguida Centre',
        prefecture: 'Golfe',
        region: 'Grand Lomé',
        valeur: 15971,
        inscriptions: 15971,
      },
    ],
  },
  echecs: {
    perimetre: 'Ensemble du Togo',
    classement: 'echecs',
    centres: [
      {
        rang: 1,
        code: '20003',
        nom: 'EPP Worgou G/A',
        prefecture: 'Tône',
        region: 'Savanes',
        valeur: 161,
        inscriptions: 12404,
      },
    ],
  },
  rejets: { perimetre: 'Ensemble du Togo', classement: 'rejets', centres: [] },
  remontee: {
    perimetre: 'Ensemble du Togo',
    classement: 'remontee',
    centres: [
      {
        rang: 1,
        code: '20004',
        nom: 'Complexe scolaire Les Lauriers',
        prefecture: 'Golfe',
        region: 'Grand Lomé',
        valeur: 138,
        inscriptions: 9120,
      },
    ],
  },
};

/**
 * Motifs : totaux égaux aux rejetés (86 496), échoués (9 218) et en cours (123 639, dont 59 264 bloqués) du bloc
 * Devenir par défaut ; lignes du plus fréquent au moins fréquent, comme l'API.
 */
export const MOTIFS: MotifsArret = {
  perimetre: 'Ensemble du Togo',
  calculeLe: '2026-01-14T11:45:00Z',
  seuilJours: 30,
  totalRejets: 86496,
  totalEchecs: 9218,
  totalEnCours: 123639,
  bloques: 59264,
  rejets: [
    {
      motif: 'REFUS_SUPERVISEUR',
      libelle: 'Rejeté par le superviseur du centre',
      commentaire: 'Rejected by Supervisor',
      piste:
        'Le superviseur a refusé le paquet au poste ; MOSIP ne transmet pas sa raison. La personne doit se réenrôler.',
      stage: 'PacketValidatorStage',
      stageLibelle: 'Validation du paquet',
      autresEtapes: 0,
      inscriptions: 50133,
      bloques: 0,
    },
    {
      motif: 'DOUBLON_ABIS',
      libelle: 'Doublon biométrique trouvé par l’ABIS',
      commentaire: 'Biometric Duplicate was Found in ABIS',
      piste: 'La personne est déjà enregistrée (empreintes, iris ou visage) : demande en double.',
      stage: 'DemoDedupeStage',
      stageLibelle: 'Déduplication démographique',
      autresEtapes: 0,
      inscriptions: 20541,
      bloques: 0,
    },
    {
      motif: 'DOUBLON_VERIFICATEUR',
      libelle: 'Doublon confirmé par le vérificateur',
      commentaire: 'Match Found by Manual Verifier',
      piste: 'Après comparaison manuelle avec un dossier existant : même personne.',
      stage: 'ManualVerificationStage',
      stageLibelle: 'Vérification manuelle',
      autresEtapes: 6,
      inscriptions: 14752,
      bloques: 0,
    },
    {
      motif: null,
      libelle: 'Autres cas',
      commentaire: null,
      piste: null,
      stage: null,
      stageLibelle: null,
      autresEtapes: 0,
      inscriptions: 1070,
      bloques: 0,
    },
  ],
  echecs: [
    {
      motif: 'BIOMETRIE_NON_CONCORDANTE',
      libelle: 'Authentification biométrique échouée (type non précisé)',
      commentaire: 'Biometric data did not match',
      piste:
        'Contrôle de la personne qui valide le paquet (agent, superviseur ou parent pour un enfant) ; MOSIP ne dit pas laquelle.',
      stage: 'OSIValidatorStage',
      stageLibelle: 'Validation de l’agent, du superviseur et du parent',
      autresEtapes: 0,
      inscriptions: 8165,
      bloques: 0,
    },
    {
      motif: 'PAQUET_INTROUVABLE',
      libelle: 'Paquet introuvable à l’arrivée',
      commentaire: 'Packet not found in Landing Zone',
      piste: 'Synchronisé mais jamais déposé sur le serveur : le renvoyer depuis le poste.',
      stage: 'PacketUploaderStage',
      stageLibelle: 'Envoi du paquet',
      autresEtapes: 0,
      inscriptions: 1053,
      bloques: 0,
    },
  ],
  enCours: [
    {
      motif: 'FILE_VERIF_MANUELLE',
      libelle: 'En file d’attente de vérification manuelle',
      commentaire: 'Manual verification Sent to queue',
      piste: 'Doublon possible : un vérificateur doit trancher.',
      stage: 'BioDedupeStage',
      stageLibelle: 'Déduplication biométrique',
      autresEtapes: 0,
      inscriptions: 112618,
      bloques: 58834,
    },
    {
      motif: 'RECU_EN_ATTENTE',
      libelle: 'Paquet reçu, en attente de traitement',
      commentaire: 'Packet is Uploaded to Landing Zone / Packet Store',
      piste: "Normal s'il est récent.",
      stage: 'PacketReceiverStage',
      stageLibelle: 'Réception du paquet',
      autresEtapes: 0,
      inscriptions: 7476,
      bloques: 0,
    },
    {
      motif: null,
      libelle: 'Autres cas',
      commentaire: null,
      piste: null,
      stage: null,
      stageLibelle: null,
      autresEtapes: 0,
      inscriptions: 3545,
      bloques: 430,
    },
  ],
  // Partie des en cours (onglet du 02/11/2026) : 7 783 = enReprocessing du Devenir.
  totalReprocessing: 7783,
  bloquesReprocessing: 6902,
  reprocessing: [
    {
      motif: 'ERREUR_VERIF_MANUELLE',
      libelle: 'Erreur lors de la vérification manuelle',
      commentaire: 'Error in manual verification',
      piste: 'Dossier bloqué dans la file : à signaler à l’équipe MOSIP.',
      stage: 'ManualVerificationStage',
      stageLibelle: 'Vérification manuelle',
      autresEtapes: 0,
      inscriptions: 7263,
      bloques: 6620,
    },
    {
      motif: null,
      libelle: 'Autres cas',
      commentaire: null,
      piste: null,
      stage: null,
      stageLibelle: null,
      autresEtapes: 0,
      inscriptions: 520,
      bloques: 282,
    },
  ],
};

export const DELAIS: DelaisTraitement = {
  perimetre: 'Ensemble du Togo',
  receptionNiu: { paquets: 3058886, medianeH: 8, centile90H: 240, moins24h: 2500000 },
  enrolementReception: { paquets: 3278239, medianeH: 5, centile90H: 30, moins24h: 3009423 },
};

export const SYNCHRONISATION: SynchronisationNonRecue = {
  perimetre: 'Ensemble du Togo',
  calculeLe: '2026-01-14T11:45:00Z',
  nonRecus: 932,
  plusDe7Jours: 505,
  plusAncienneLe: '2025-01-06T08:00:00Z',
};

export const PREINSCRIPTIONS: Preinscriptions = {
  perimetre: 'Ensemble du Togo',
  disponible: true,
  demandes: 606850,
  rendezVousReserves: 546964,
  enAttenteRendezVous: 59886,
  expirees: 0,
  annulees: 0,
  honorees: 450123,
  nonClassees: 0,
  femmes: null,
  hommes: null,
  derniereDemande: '2026-01-14T11:28:00Z',
};

/** Pyramide de la maquette (en NIU), de la plus jeune à la plus âgée, comme l'API. */
export const PROFIL_PREINSCRIPTIONS: ProfilPreinscriptions = {
  perimetre: 'Ensemble du Togo',
  du: null,
  au: null,
  disponible: true,
  tranches: [
    { tranche: '0-5', femmes: 19000, hommes: 20000 },
    { tranche: '6-14', femmes: 43000, hommes: 45000 },
    { tranche: '15-18', femmes: 27000, hommes: 26000 },
    { tranche: '19-25', femmes: 62000, hommes: 57000 },
    { tranche: '26-35', femmes: 79000, hommes: 70000 },
    { tranche: '36-45', femmes: 46000, hommes: 42000 },
    { tranche: '46-60', femmes: 27000, hommes: 23000 },
    { tranche: '60+', femmes: 11000, hommes: 9850 },
    { tranche: 'inconnu', femmes: 1837, hommes: 2583 },
  ],
  nonRenseignes: 0,
  nationalites: [
    { nom: 'TOGO', demandes: 603120 },
    { nom: 'BENIN', demandes: 2100 },
    { nom: 'GHANA', demandes: 900 },
    { nom: 'NIGERIA', demandes: 420 },
    { nom: 'BURKINA FASO', demandes: 210 },
    { nom: 'Autres', demandes: 100 },
  ],
};

export const AGE_SEXE: AgeSexe = {
  perimetre: 'Ensemble du Togo',
  disponible: true,
  nonRenseignes: 0,
  // Somme égale à celle de la pyramide (3 058 886) : contrôle de l'API
  nationalites: [
    { nom: 'Togo', niuGeneres: 3011220 },
    { nom: 'BENIN', niuGeneres: 21460 },
    { nom: 'GHANA', niuGeneres: 12730 },
    { nom: 'NIGER', niuGeneres: 6120 },
    { nom: 'BURKINA FASO', niuGeneres: 4310 },
    { nom: 'Autres', niuGeneres: 3046 },
  ],
  tranches: [
    { tranche: '0-5', femmes: 33647, hommes: 36707 },
    { tranche: '6-14', femmes: 131532, hommes: 140709 },
    { tranche: '15-18', femmes: 116238, hommes: 113178 },
    { tranche: '19-25', femmes: 287535, hommes: 256946 },
    { tranche: '26-35', femmes: 385419, hommes: 339538 },
    { tranche: '36-45', femmes: 284476, hommes: 247770 },
    { tranche: '46-60', femmes: 256946, hommes: 220240 },
    { tranche: '60+', femmes: 125415, hommes: 82590 },
  ],
};

/** Impression des cartes (lot 8c) : chiffres publiés le 03/11/2026, semaines de la maquette (dernière : 05/01/2026). */
export const IMPRESSION = {
  perimetre: 'Ensemble du Togo',
  disponible: true,
  demandes: 6195305,
  envoyees: 6192991,
  enAttente: 2306,
  rejetees: 8,
  nonClassees: 0,
  annulees: 693,
  derniereRejetee: '2026-01-07',
  expediees: 6107359,
  remises: 4643568,
  remisesHorsLigne: 4446166,
  remisesEnLigne: 197370,
  remisesSupport: 32,
  remisesAutre: 0,
  aRemettre: 1463791,
  delaiMedianJours: 31,
  erreursIdps: 172354,
  derniereErreurIdps: '2026-01-09',
  niuSansCommande: 58,
  niuSansCommandePlus7j: 3,
};

const ANNULATIONS = {
  perimetre: 'Ensemble du Togo',
  total: 693,
  motifs: [
    { code: 'CANCEL_PHOTO', libelle: 'Photo à reprendre', demandes: 643 },
    { code: 'CANCEL_SEX', libelle: 'Sexe à corriger', demandes: 36 },
    { code: 'CANCEL_NAME', libelle: 'Nom à corriger', demandes: 10 },
    {
      code: 'PERSONALIZATION_MANAGER_REPORTED_ERROR',
      libelle: 'Erreur signalée à la personnalisation',
      demandes: 4,
    },
  ],
};

const SEMAINES_CARTES = {
  perimetre: 'Ensemble du Togo',
  semaines: LUNDIS.map((lundi, i) => ({
    lundi,
    dansPeriode: true,
    demandes: 29000 + 300 * i,
    expediees: 28500 + 250 * i,
    rejetees: i === 11 ? 1 : 0,
    annulees: i % 3,
  })),
};

const ligneCartes = (code: string, nom: string, niveau: string, expediees: number, remises: number) => ({
  code,
  nom,
  niveau,
  horsReferentiel: false,
  ouvrable: niveau === 'region',
  expediees,
  remises,
  aRemettre: expediees - remises,
});

const territoireCartes = (
  perimetre: string,
  zone: string | null,
  lignes: ReturnType<typeof ligneCartes>[],
) => ({
  perimetre,
  zone,
  niveau: zone ? 'region' : null,
  ascendants: [],
  expediees: lignes.reduce((t, l) => t + l.expediees, 0),
  remises: lignes.reduce((t, l) => t + l.remises, 0),
  aRemettre: lignes.reduce((t, l) => t + l.aRemettre, 0),
  lignes,
});

const CARTES_NATIONAL = territoireCartes('Ensemble du Togo', null, [
  ligneCartes('SAV', 'Savanes', 'region', 423590, 188796),
  ligneCartes('KAR', 'Kara', 'region', 362000, 290000),
  ligneCartes('CEN', 'Centrale', 'region', 292000, 230000),
  ligneCartes('PLA', 'Plateaux', 'region', 563000, 440000),
  ligneCartes('MAR', 'Maritime', 'region', 486000, 380000),
  ligneCartes('GLO', 'Grand Lomé', 'region', 975000, 760000),
]);

const CARTES_SAVANES = territoireCartes('Savanes', 'SAV', [
  ligneCartes('SAV-01', 'Cinkassé', 'prefecture', 70000, 30000),
  ligneCartes('SAV-02', 'Tône', 'prefecture', 180000, 82796),
  ligneCartes('SAV-03', 'Kpendjal', 'prefecture', 60000, 26000),
  ligneCartes('SAV-04', 'Tandjouaré', 'prefecture', 50000, 20000),
  ligneCartes('SAV-05', 'Oti', 'prefecture', 63590, 30000),
]);

const ATTENTE = {
  perimetre: 'Ensemble du Togo',
  calculeLe: '2026-01-14',
  aRemettre: 1463791,
  tranches: [
    { code: 'moins_30j', depuisJours: 0, avantJours: 30, cartes: 121430 },
    { code: '30_90j', depuisJours: 30, avantJours: 90, cartes: 61748 },
    { code: '90_180j', depuisJours: 90, avantJours: 180, cartes: 61014 },
    { code: 'plus_180j', depuisJours: 180, avantJours: null, cartes: 1219599 },
  ],
};

const CENTRES_CARTES = {
  perimetre: 'Ensemble du Togo',
  centres: [
    {
      rang: 1,
      code: '10011',
      nom: 'EPP Doumassesse',
      prefecture: 'Golfe',
      region: 'Grand Lomé',
      remises: 31289,
      expediees: 44370,
    },
    {
      rang: 2,
      code: '10012',
      nom: 'CEG Baguida',
      prefecture: 'Golfe',
      region: 'Grand Lomé',
      remises: 11818,
      expediees: 16033,
    },
  ],
};

/** Authentifications (lot 9c) : chiffres du relevé du 03/11/2026 sur 30 jours (maquette validée le 04/11/2026). */
export const USAGERS_AUTH = {
  perimetre: 'Ensemble du Togo',
  disponible: true,
  requetes: 2186,
  reussies: 1538,
  echouees: 648,
  autresStatuts: 0,
  biometriques: 1,
  otp: 1955,
  demographiquesEtCombinees: 0,
  sansMode: 230,
  nonClassees: 0,
  partenairesRaccordes: 1,
  requetesPartenaires: 1645,
  partenaires: ['Atos'],
  demandesOtp: 2732,
  demandesOtpEnvoyees: 2380,
  codesOtp: 83873,
  codesOtpUtilises: 50781,
};

const TYPES_AUTH = {
  types: [
    { code: 'biometrique', requetes: 1, echecs: 1 },
    { code: 'otp', requetes: 1955, echecs: 417 },
    { code: 'demographique', requetes: 0, echecs: 0 },
    { code: 'combinee', requetes: 0, echecs: 0 },
    { code: 'sans_mode', requetes: 230, echecs: 230 },
    { code: 'non_classe', requetes: 0, echecs: 0 },
  ],
};

const CAUSES_USAGERS = {
  perimetre: 'usagers',
  echecs: 648,
  motifs: [
    { code: 'OTP_REFUSE', libelle: 'Code OTP ou eKYC refusé', echecs: 417 },
    { code: 'SANS_MODE', libelle: "Aucun mode d'authentification demandé", echecs: 230 },
    { code: 'AUTRE', libelle: 'Motif non répertorié', echecs: 1 },
  ],
};

const CAUSES_PAQUETS = {
  perimetre: 'paquets',
  echecs: 144898,
  motifs: [
    { code: 'BIO_NON_CONCORDANTE', libelle: 'Biométrie non concordante', echecs: 106076 },
    { code: 'BIO_ABSENTE', libelle: "Biométrie absente du dossier d'authentification", echecs: 21151 },
    { code: 'NIU_ABSENT', libelle: "NIU absent de la base d'authentification", echecs: 17637 },
    { code: 'MODALITE_VERROUILLEE', libelle: 'Modalité verrouillée par le résident', echecs: 34 },
  ],
};

const PARTENAIRES_AUTH = {
  partenairesRaccordes: 1,
  appelants: [
    { canal: 'partenaire', nom: 'Atos', requetes: 1645, reussies: 1142, demandesOtp: 2159, derniereRequete: '2026-01-14' },
    { canal: 'portail', nom: 'Portail du résident', requetes: 517, reussies: 377, demandesOtp: 560, derniereRequete: '2026-01-14' },
    { canal: 'ussd', nom: 'USSD', requetes: 24, reussies: 19, demandesOtp: 13, derniereRequete: '2026-01-12' },
  ],
};

const SEMAINES_AUTH = {
  semaines: LUNDIS.map((lundi, i) => ({ lundi, dansPeriode: true, reussies: 360 + i, echouees: 150 + i })),
};

const PAQUETS_AUTH = { disponible: true, verifications: 170151, reussies: 25253, echouees: 144898, autresStatuts: 0 };

/** Valeur renvoyée, ou calculée depuis l'adresse et la requête (corps d'un POST) ; undefined répond 404. */
type Reponse = unknown | ((url: URL, init?: RequestInit) => unknown);

const PAR_DEFAUT: Record<string, Reponse> = {
  '/meta': META,
  '/meta/regions': REGIONS,
  '/enrolement/devenir': {
    perimetre: 'Ensemble du Togo',
    inscriptions: 3278239,
    niuGeneres: 3058886,
    enCours: 123639,
    echouees: 9218,
    rejetees: 86496,
    nonClassees: 0,
    bloques: 59264,
    enReprocessing: 7783,
    demandesMiseAJour: 12811,
    demandesNiuPerdu: 1964,
  },
  '/enrolement/semaines': SEMAINES,
  '/enrolement/jours': JOURS,
  '/enrolement/suivi': (_url: URL, init?: RequestInit) =>
    JSON.parse(String(init?.body ?? '{}')).rid === RID_CONNU ? SUIVI : undefined,
  '/enrolement/motifs': MOTIFS,
  '/enrolement/delais': DELAIS,
  '/enrolement/synchronisation': SYNCHRONISATION,
  '/enrolement/territoire': (url: URL) =>
    TERRITOIRES[url.searchParams.get('zone') ?? ''] ?? TERRITOIRE_NATIONAL,
  '/enrolement/centres': (url: URL) => CENTRES[url.searchParams.get('classement') ?? 'inscriptions'],
  '/enrolement/preinscriptions': PREINSCRIPTIONS,
  '/enrolement/preinscriptions/profil': PROFIL_PREINSCRIPTIONS,
  '/cartes/impression': IMPRESSION,
  '/cartes/annulations': ANNULATIONS,
  '/cartes/semaines': SEMAINES_CARTES,
  '/cartes/territoire': (url: URL) =>
    url.searchParams.get('zone') === 'SAV' ? CARTES_SAVANES : CARTES_NATIONAL,
  '/cartes/attente': ATTENTE,
  '/cartes/centres': CENTRES_CARTES,
  '/authentifications/usagers': USAGERS_AUTH,
  '/authentifications/types': TYPES_AUTH,
  '/authentifications/causes': (url: URL) =>
    url.searchParams.get('perimetre') === 'paquets' ? CAUSES_PAQUETS : CAUSES_USAGERS,
  '/authentifications/partenaires': PARTENAIRES_AUTH,
  '/authentifications/semaines': SEMAINES_AUTH,
  '/authentifications/paquets': PAQUETS_AUTH,
  '/authentifications/exploration': (url: URL) => {
    const paquets = url.searchParams.get('perimetre') === 'paquets';
    const par = url.searchParams.get('par') ?? 'total';
    const chiffres = (requetes: number, reussies: number) => ({ requetes, reussies, echouees: requetes - reussies });
    const lignes =
      par === 'mois'
        ? [
            { cle: '2025-12', libelle: '2025-12', chiffres: chiffres(1200, 700) },
            { cle: '2026-01', libelle: '2026-01', chiffres: chiffres(986, 838) },
          ]
        : par === 'appelant'
          ? paquets
            ? [{ cle: 'Traitement des paquets', libelle: 'Traitement des paquets', chiffres: chiffres(170151, 25253) }]
            : [
                { cle: 'Atos', libelle: 'Atos', chiffres: chiffres(1645, 1142) },
                { cle: 'Portail du résident', libelle: 'Portail du résident', chiffres: chiffres(517, 377) },
              ]
          : [];
    return {
      perimetre: paquets ? 'paquets' : 'usagers',
      par,
      lignes,
      total: paquets ? chiffres(170151, 25253) : chiffres(2186, 1538),
      valeurs: {
        types: paquets ? ['biometrique'] : ['biometrique', 'otp', 'sans_mode'],
        motifs: paquets ? CAUSES_PAQUETS.motifs : CAUSES_USAGERS.motifs,
        appelants: paquets ? ['Traitement des paquets'] : ['Atos', 'Portail du résident', 'USSD'],
      },
    };
  },
  '/enrolement/age-sexe': (url: URL) =>
    url.searchParams.get('zone') === 'SAV'
      ? {
          ...AGE_SEXE,
          perimetre: 'Savanes',
          tranches: AGE_SEXE.tranches.map((t) => ({
            ...t,
            femmes: Math.round((t.femmes ?? 0) * 0.14),
            hommes: Math.round((t.hommes ?? 0) * 0.14),
          })),
        }
      : AGE_SEXE,
};

/**
 * Remplace fetch : chaque chemin de /api/v1 répond la valeur donnée (ou calculée depuis l'adresse) ; un chemin
 * inconnu répond 404. Renvoie la liste des adresses appelées.
 */
export function simulerApi(reponses: Record<string, Reponse> = {}): URL[] {
  const appels: URL[] = [];
  const toutes = { ...PAR_DEFAUT, ...reponses };
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: URL, init?: RequestInit) => {
      appels.push(url);
      const reponse = toutes[url.pathname.replace(/^.*\/api\/v1/, '')];
      if (reponse === undefined) return new Response('', { status: 404 });
      const corps = typeof reponse === 'function' ? reponse(url, init) : reponse;
      if (corps === undefined) return new Response('', { status: 404 });
      return new Response(JSON.stringify(corps), { headers: { 'Content-Type': 'application/json' } });
    }),
  );
  return appels;
}

/** Affiche l'application à cette adresse ; renvoie le routeur pour lire l'adresse courante. */
export function afficher(adresse: string) {
  const routeur = creerRouteur(createMemoryHistory({ initialEntries: [adresse] }));
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <RouterProvider router={routeur} />
    </QueryClientProvider>,
  );
  return routeur;
}
