import type { Page } from '@playwright/test';

/**
 * API simulée des parcours Playwright pour la page Enrôlement (chiffres de la maquette, dernière donnée le
 * 14/01/2026). Chaque test l'installe avec simulerEnrolement(page) ; aucun appel ne sort du navigateur.
 */
const REGIONS = [
  { code: 'SAV', nom: 'Savanes' },
  { code: 'KAR', nom: 'Kara' },
  { code: 'CEN', nom: 'Centrale' },
  { code: 'PLA', nom: 'Plateaux' },
  { code: 'MAR', nom: 'Maritime' },
  { code: 'GLO', nom: 'Grand Lomé' },
];

const zone = (code: string, nom: string, niveau: string, ins: number, niu: number, rej: number) => {
  const echouees = Math.round(ins * 0.003);
  return {
    code,
    nom,
    niveau,
    horsReferentiel: false,
    inscriptions: ins,
    niuGeneres: niu,
    rejetees: rej,
    echouees,
    enCours: ins - niu - rej - echouees,
    nonClassees: 0,
    preinscriptions: Math.round(ins * 0.4),
    ouvrable: niveau !== 'centre',
  };
};

type Ligne = ReturnType<typeof zone>;

const territoire = (perimetre: string, code: string | null, lignes: Ligne[]) => ({
  perimetre,
  zone: code,
  niveau: code ? 'region' : null,
  ascendants: [],
  inscriptions: lignes.reduce((s, l) => s + l.inscriptions, 0),
  niuGeneres: lignes.reduce((s, l) => s + l.niuGeneres, 0),
  enCours: lignes.reduce((s, l) => s + l.enCours, 0),
  echouees: lignes.reduce((s, l) => s + l.echouees, 0),
  rejetees: lignes.reduce((s, l) => s + l.rejetees, 0),
  nonClassees: 0,
  preinscriptions: lignes.reduce((s, l) => s + l.preinscriptions, 0),
  lignes,
});

const NATIONAL = territoire('Ensemble du Togo', null, [
  zone('SAV', 'Savanes', 'region', 450239, 413573, 16072),
  zone('KAR', 'Kara', 'region', 386000, 358514, 11069),
  zone('CEN', 'Centrale', 'region', 312000, 288857, 9516),
  zone('PLA', 'Plateaux', 'region', 598000, 556639, 16541),
  zone('MAR', 'Maritime', 'region', 512000, 479495, 12381),
  zone('GLO', 'Grand Lomé', 'region', 1020000, 961808, 20917),
]);

const KARA = territoire('Kara', 'KAR', [
  zone('KAR-01', 'Kéran', 'prefecture', 28000, 25900, 896),
  zone('KAR-02', 'Doufelgou', 'prefecture', 46000, 42700, 1426),
  zone('KAR-03', 'Binah', 'prefecture', 50000, 46500, 1450),
  zone('KAR-04', 'Dankpen', 'prefecture', 36000, 33200, 1224),
  zone('KAR-05', 'Kozah', 'prefecture', 132000, 123300, 3432),
  zone('KAR-06', 'Assoli', 'prefecture', 24000, 22300, 744),
  zone('KAR-07', 'Bassar', 'prefecture', 70000, 64614, 1897),
]);

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
const INSCRIPTIONS = [31800, 31600, 37800, 38600, 36400, 38300, 40400, 37400, 38100, 23200, 18100, 20230];
const NIU = [27300, 29100, 35100, 35000, 35500, 36200, 35600, 35800, 37300, 21100, 18300, 17626];

const centre = (
  rang: number,
  code: string,
  nom: string,
  prefecture: string,
  region: string,
  valeur: number,
) => ({
  rang,
  code,
  nom,
  prefecture,
  region,
  valeur,
  inscriptions: valeur,
});

const CENTRES: Record<string, unknown[]> = {
  inscriptions: [
    centre(1, '20101', 'EPP Doumassesse I G/B', 'Golfe', 'Grand Lomé', 43534),
    centre(2, '20102', 'CEG Baguida Centre, Port de pêche', 'Golfe', 'Grand Lomé', 15971),
    centre(3, '20103', 'EPP Worgou G/A', 'Tône', 'Savanes', 12404),
    centre(4, '20104', 'EPP Gbetsogbe, Port autonome', 'Golfe', 'Grand Lomé', 11919),
    centre(5, '20105', 'Lycée Nassable', 'Tône', 'Savanes', 10109),
  ],
  echecs: [centre(1, '20103', 'EPP Worgou G/A', 'Tône', 'Savanes', 161)],
  rejets: [centre(1, '20105', 'Lycée Nassable', 'Tône', 'Savanes', 412)],
  remontee: [centre(1, '20104', 'EPP Gbetsogbe, Port autonome', 'Golfe', 'Grand Lomé', 138)],
};

// Lot 5 : motifs d'arrêt (rejetés, échoués, en cours dont bloqués), délais, synchronisés non reçus.
const MOTIFS = {
  perimetre: 'Ensemble du Togo',
  calculeLe: '2026-01-14T11:45:00Z',
  seuilJours: 30,
  totalRejets: 159296,
  totalEchecs: 104478,
  totalEnCours: 85050,
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
      inscriptions: 91255,
      bloques: 0,
    },
    {
      motif: 'DOUBLON_ABIS',
      libelle: 'Doublon biométrique trouvé par l’ABIS',
      commentaire: 'Biometric Duplicate was Found in ABIS',
      piste: 'La personne est déjà enregistrée (empreintes, iris ou visage) : demande en double.',
      stage: 'DemoDedupeStage',
      stageLibelle: 'Déduplication démographique',
      inscriptions: 37849,
      bloques: 0,
    },
    {
      motif: 'DOUBLON_VERIFICATEUR',
      libelle: 'Doublon confirmé par le vérificateur',
      commentaire: 'Match Found by Manual Verifier',
      piste: 'Après comparaison manuelle avec un dossier existant : même personne.',
      stage: 'ManualVerificationStage',
      stageLibelle: 'Vérification manuelle',
      inscriptions: 28539,
      bloques: 0,
    },
    {
      motif: 'DONNEES_INVALIDES_NIU',
      libelle: 'Création du NIU refusée : donnée invalide',
      commentaire: 'UIN Generation failed - Invalid Input Parameter',
      piste:
        'MOSIP nomme le champ en cause (date de délivrance, attributs vérifiés…) : erreur de saisie ou de format.',
      stage: 'UinGeneratorStage',
      stageLibelle: 'Génération du NIU',
      inscriptions: 1184,
      bloques: 0,
    },
    {
      motif: null,
      libelle: 'Autres cas',
      commentaire: null,
      piste: null,
      stage: null,
      stageLibelle: null,
      inscriptions: 469,
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
      inscriptions: 80000,
      bloques: 0,
    },
    {
      motif: 'IRIS_NON_CONCORDANT',
      libelle: 'Iris non concordant',
      commentaire: 'Biometric data - Iris did not match',
      piste:
        'Qualité de capture de l’iris au poste, ou iris de la personne qui valide (agent, superviseur ou parent) mal enregistré ; MOSIP ne dit pas laquelle.',
      stage: 'OSIValidatorStage',
      stageLibelle: 'Validation de l’agent, du superviseur et du parent',
      inscriptions: 12800,
      bloques: 0,
    },
    {
      motif: 'EMPREINTES_NON_CONCORDANTES',
      libelle: 'Empreintes non concordantes',
      commentaire: 'Biometric data - Finger did not match',
      piste:
        'Qualité de capture des empreintes au poste, ou empreintes de la personne qui valide (agent, superviseur ou parent) mal enregistrées ; MOSIP ne dit pas laquelle.',
      stage: 'OSIValidatorStage',
      stageLibelle: 'Validation de l’agent, du superviseur et du parent',
      inscriptions: 2760,
      bloques: 0,
    },
    {
      motif: 'PAQUET_INTROUVABLE',
      libelle: 'Paquet introuvable à l’arrivée',
      commentaire: 'Packet not found in Landing Zone',
      piste: 'Synchronisé mais jamais déposé sur le serveur : le renvoyer depuis le poste.',
      stage: 'PacketUploaderStage',
      stageLibelle: 'Envoi du paquet',
      inscriptions: 3200,
      bloques: 0,
    },
    {
      motif: 'NIU_VALIDEUR_INTROUVABLE',
      libelle: 'NIU de la personne qui valide introuvable',
      commentaire: 'UIN not available in database',
      piste: 'L’agent, le superviseur ou le parent n’a pas de NIU dans le registre.',
      stage: 'OSIValidatorStage',
      stageLibelle: 'Validation de l’agent, du superviseur et du parent',
      inscriptions: 1150,
      bloques: 0,
    },
    {
      motif: null,
      libelle: 'Autres cas',
      commentaire: null,
      piste: null,
      stage: null,
      stageLibelle: null,
      inscriptions: 4568,
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
      inscriptions: 51696,
      bloques: 51200,
    },
    {
      motif: 'ETAPE_FRANCHIE',
      libelle: 'Étape réussie, en attente de l’étape suivante',
      commentaire: '… is Successful / Unique Match was Found / Notification received',
      piste: 'Normal s’il est récent ; bloqué au-delà de 30 jours.',
      stage: 'PacketValidatorStage',
      stageLibelle: 'Validation du paquet',
      inscriptions: 21406,
      bloques: 1364,
    },
    {
      motif: 'ERREUR_VERIF_MANUELLE',
      libelle: 'Erreur lors de la vérification manuelle',
      commentaire: 'Error in manual verification',
      piste: 'Dossier bloqué dans la file : à signaler à l’équipe MOSIP.',
      stage: 'ManualVerificationStage',
      stageLibelle: 'Vérification manuelle',
      inscriptions: 6792,
      bloques: 6700,
    },
    {
      motif: 'RECU_EN_ATTENTE',
      libelle: 'Paquet reçu, en attente de traitement',
      commentaire: 'Packet is Uploaded to Landing Zone / Packet Store',
      piste: 'Normal s’il est récent.',
      stage: 'PacketReceiverStage',
      stageLibelle: 'Réception du paquet',
      inscriptions: 4489,
      bloques: 0,
    },
    {
      motif: null,
      libelle: 'Autres cas',
      commentaire: null,
      piste: null,
      stage: null,
      stageLibelle: null,
      inscriptions: 667,
      bloques: 0,
    },
  ],
};
const DELAIS = {
  perimetre: 'Ensemble du Togo',
  receptionNiu: { paquets: 6000000, medianeH: 8, centile90H: 240, moins24h: 4800000 },
  enrolementReception: { paquets: 6380570, medianeH: 5, centile90H: 30, moins24h: 5858637 },
};
const SYNCHRONISATION = {
  perimetre: 'Ensemble du Togo',
  calculeLe: '2026-01-14T11:45:00Z',
  nonRecus: 932,
  plusDe7Jours: 505,
  plusAncienneLe: '2025-01-06T08:00:00Z',
};

// Pyramide de la maquette (en NIU), de la plus jeune à la plus âgée, comme l'API.
const PYRAMIDE: [string, number, number][] = [
  ['0-5', 33647, 36707],
  ['6-14', 131532, 140709],
  ['15-18', 116238, 113178],
  ['19-25', 287535, 256946],
  ['26-35', 385419, 339538],
  ['36-45', 284476, 247770],
  ['46-60', 256946, 220240],
  ['60+', 125415, 82590],
];

export async function simulerEnrolement(page: Page) {
  await page.route('**/api/v1/enrolement/motifs*', (route) => route.fulfill({ json: MOTIFS }));
  await page.route('**/api/v1/enrolement/delais*', (route) => route.fulfill({ json: DELAIS }));
  await page.route('**/api/v1/enrolement/synchronisation*', (route) =>
    route.fulfill({ json: SYNCHRONISATION }),
  );
  await page.route('**/api/v1/enrolement/preinscriptions/profil*', (route) =>
    route.fulfill({
      json: {
        perimetre: 'Ensemble du Togo',
        du: null,
        au: null,
        disponible: true,
        tranches: PYRAMIDE.map(([tranche, femmes, hommes]) => ({
          tranche,
          femmes: Math.round(femmes * 0.2),
          hommes: Math.round(hommes * 0.2),
        })).concat([{ tranche: 'inconnu', femmes: 1837, hommes: 2583 }]),
        nonRenseignes: 0,
        nationalites: [
          { nom: 'TOGO', demandes: 603120 },
          { nom: 'BENIN', demandes: 2100 },
          { nom: 'GHANA', demandes: 900 },
          { nom: 'Autres', demandes: 730 },
        ],
      },
    }),
  );
  await page.route('**/api/v1/enrolement/preinscriptions*', (route) =>
    route.fulfill({
      json: {
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
      },
    }),
  );
  await page.route('**/api/v1/enrolement/age-sexe*', (route) => {
    const kara = new URL(route.request().url()).searchParams.get('zone') === 'KAR';
    const part = kara ? 0.12 : 1;
    route.fulfill({
      json: {
        perimetre: kara ? 'Kara' : 'Ensemble du Togo',
        disponible: true,
        nonRenseignes: 0,
        tranches: PYRAMIDE.map(([tranche, femmes, hommes]) => ({
          tranche,
          femmes: Math.round(femmes * part),
          hommes: Math.round(hommes * part),
        })),
      },
    });
  });
  await page.route('**/api/v1/meta/regions', (route) => route.fulfill({ json: REGIONS }));
  await page.route('**/api/v1/enrolement/semaines*', (route) =>
    route.fulfill({
      json: {
        perimetre: 'Ensemble du Togo',
        niuDisponibles: true,
        semaines: LUNDIS.map((lundi, i) => ({
          lundi,
          dansLaPeriode: true,
          inscriptions: INSCRIPTIONS[i],
          niuGeneres: NIU[i],
        })),
      },
    }),
  );
  await page.route('**/api/v1/enrolement/territoire*', (route) =>
    route.fulfill({
      json: new URL(route.request().url()).searchParams.get('zone') === 'KAR' ? KARA : NATIONAL,
    }),
  );
  await page.route('**/api/v1/enrolement/centres*', (route) => {
    const url = new URL(route.request().url());
    const classement = url.searchParams.get('classement') ?? 'inscriptions';
    const kara = url.searchParams.get('zone') === 'KAR';
    route.fulfill({
      json: {
        perimetre: kara ? 'Kara' : 'Ensemble du Togo',
        classement,
        centres: kara ? [] : CENTRES[classement],
      },
    });
  });
}
