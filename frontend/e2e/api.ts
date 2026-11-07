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
      autresEtapes: 0,
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
      autresEtapes: 0,
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
      autresEtapes: 6,
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
      autresEtapes: 0,
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
      autresEtapes: 0,
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
      autresEtapes: 0,
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
      autresEtapes: 0,
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
      autresEtapes: 0,
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
      autresEtapes: 0,
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
      autresEtapes: 0,
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
      autresEtapes: 0,
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
      autresEtapes: 0,
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
      autresEtapes: 0,
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
      autresEtapes: 0,
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
      autresEtapes: 0,
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
      autresEtapes: 0,
      inscriptions: 667,
      bloques: 0,
    },
  ],
  // Onglet « En reprocessing » (02/11/2026) : partie des en cours.
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
        nationalites: [
          { nom: 'Togo', niuGeneres: Math.round(3011220 * part) },
          { nom: 'BENIN', niuGeneres: Math.round(21460 * part) },
          { nom: 'GHANA', niuGeneres: Math.round(12730 * part) },
          { nom: 'Autres', niuGeneres: Math.round(13476 * part) },
        ],
      },
    });
  });
  await page.route('**/api/v1/meta/regions', (route) => route.fulfill({ json: REGIONS }));
  // 28 jours jusqu'à aujourd'hui (heure du Togo), le jour en cours plus faible.
  await page.route('**/api/v1/enrolement/jours*', (route) => {
    const aujourdhui = new Date(new Date().toISOString().slice(0, 10) + 'T00:00:00Z');
    const jours = Array.from({ length: 28 }, (_, i) => {
      const d = new Date(aujourdhui);
      d.setUTCDate(aujourdhui.getUTCDate() - 27 + i);
      const weekEnd = d.getUTCDay() === 0 || d.getUTCDay() === 6;
      const base = i === 27 ? 2134 : weekEnd ? 1500 : 4600 + ((i * 137) % 700);
      return { jour: d.toISOString().slice(0, 10), inscriptions: base, niuGeneres: Math.round(base * 0.63) };
    });
    return route.fulfill({
      json: {
        perimetre: 'Ensemble du Togo',
        aujourdhui: jours[27].jour,
        niuDisponibles: true,
        jours,
      },
    });
  });
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
  // Exploration de l'enrôlement (lot E1) : mêmes lignes que le territoire simulé.
  await page.route('**/api/v1/enrolement/exploration*', (route) => {
    const url = new URL(route.request().url());
    const t = url.searchParams.get('zone') === 'KAR' ? KARA : NATIONAL;
    const par = url.searchParams.get('par') ?? 'total';
    const chiffres = (c: Ligne | typeof NATIONAL) => ({
      inscriptions: c.inscriptions,
      niuGeneres: c.niuGeneres,
      enCours: c.enCours,
      echouees: c.echouees,
      rejetees: c.rejetees,
      preinscriptions: c.preinscriptions,
    });
    return route.fulfill({
      json: {
        perimetre: t.perimetre,
        zone: t.zone,
        par,
        lignes:
          par === 'sous'
            ? t.lignes.map((l) => ({
                cle: l.code,
                libelle: l.nom,
                niveau: l.niveau,
                horsReferentiel: false,
                ouvrable: l.ouvrable,
                chiffres: chiffres(l),
              }))
            : [],
        total: chiffres(t),
        types: par === 'total' ? ['LOST', 'NEW', 'UPDATE'] : [],
        nationalites: par === 'total' ? ['Togo', 'Non renseignée'] : [],
      },
    });
  });
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

/** API simulée de la page Impression des cartes (lot 8c) : chiffres publiés le 03/11/2026, semaines de la maquette. */
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

const territoireCartes = (perimetre: string, zone: string | null, lignes: ReturnType<typeof ligneCartes>[]) => ({
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

const CARTES_KARA = territoireCartes('Kara', 'KAR', [
  ligneCartes('KAR-01', 'Kéran', 'prefecture', 26000, 20000),
  ligneCartes('KAR-02', 'Doufelgou', 'prefecture', 43000, 35000),
  ligneCartes('KAR-03', 'Binah', 'prefecture', 47000, 38000),
  ligneCartes('KAR-04', 'Dankpen', 'prefecture', 34000, 25000),
  ligneCartes('KAR-05', 'Kozah', 'prefecture', 124000, 102000),
  ligneCartes('KAR-06', 'Assoli', 'prefecture', 22000, 18000),
  ligneCartes('KAR-07', 'Bassar', 'prefecture', 66000, 52000),
]);

export async function simulerCartes(page: Page) {
  await page.route('**/api/v1/cartes/impression*', (route) =>
    route.fulfill({
      json: {
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
      },
    }),
  );
  await page.route('**/api/v1/cartes/annulations*', (route) =>
    route.fulfill({
      json: {
        perimetre: 'Ensemble du Togo',
        total: 693,
        motifs: [
          { code: 'CANCEL_PHOTO', libelle: 'Photo à reprendre', demandes: 643 },
          { code: 'CANCEL_SEX', libelle: 'Sexe à corriger', demandes: 36 },
          { code: 'CANCEL_NAME', libelle: 'Nom à corriger', demandes: 10 },
          { code: 'PERSONALIZATION_MANAGER_REPORTED_ERROR', libelle: 'Erreur signalée', demandes: 4 },
        ],
      },
    }),
  );
  await page.route('**/api/v1/cartes/semaines*', (route) =>
    route.fulfill({
      json: {
        perimetre: 'Ensemble du Togo',
        semaines: LUNDIS.map((lundi, i) => ({
          lundi,
          dansPeriode: true,
          demandes: [34000, 35000, 32000, 34000, 31000, 35000, 40000, 39000, 38000, 25000, 21000, 29428][i],
          expediees: [35000, 34500, 34000, 33000, 32000, 33000, 38500, 39000, 41000, 24500, 20000, 29019][i],
          rejetees: [0, 1, 0, 0, 2, 0, 0, 1, 0, 0, 0, 1][i],
          annulees: [3, 1, 4, 2, 0, 5, 2, 1, 3, 0, 2, 1][i],
        })),
      },
    }),
  );
  await page.route('**/api/v1/cartes/territoire*', (route) =>
    route.fulfill({
      json: new URL(route.request().url()).searchParams.get('zone') === 'KAR' ? CARTES_KARA : CARTES_NATIONAL,
    }),
  );
  await page.route('**/api/v1/cartes/attente*', (route) =>
    route.fulfill({
      json: {
        perimetre: 'Ensemble du Togo',
        calculeLe: '2026-01-14',
        aRemettre: 1463791,
        tranches: [
          { code: 'moins_30j', depuisJours: 0, avantJours: 30, cartes: 121430 },
          { code: '30_90j', depuisJours: 30, avantJours: 90, cartes: 61748 },
          { code: '90_180j', depuisJours: 90, avantJours: 180, cartes: 61014 },
          { code: 'plus_180j', depuisJours: 180, avantJours: null, cartes: 1219599 },
        ],
      },
    }),
  );
  await page.route('**/api/v1/cartes/centres*', (route) =>
    route.fulfill({
      json: {
        perimetre: 'Ensemble du Togo',
        centres: [
          ['10011', 'EPP Doumassesse I G/B', 'Golfe', 'Grand Lomé', 31289, 44370],
          ['10012', 'CEG Baguida Centre', 'Golfe', 'Grand Lomé', 11818, 16033],
          ['10013', 'EPP Gbetsogbe', 'Golfe', 'Grand Lomé', 9584, 12115],
          ['10014', 'Lycée Nassablé', 'Tône', 'Savanes', 6599, 10097],
          ['10015', 'Hedzranawoe (Marché)', 'Golfe', 'Grand Lomé', 6208, 9100],
        ].map(([code, nom, prefecture, region, remises, expediees], i) => ({
          rang: i + 1,
          code,
          nom,
          prefecture,
          region,
          remises,
          expediees,
        })),
      },
    }),
  );
}

/** Page Authentifications (lot 9c) : chiffres du relevé du 03/11/2026 sur 30 jours. */
export async function simulerAuthentifications(page: Page) {
  await page.route('**/api/v1/authentifications/usagers*', (route) =>
    route.fulfill({
      json: {
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
      },
    }),
  );
  await page.route('**/api/v1/authentifications/types*', (route) =>
    route.fulfill({
      json: {
        types: [
          { code: 'biometrique', requetes: 1, echecs: 1 },
          { code: 'otp', requetes: 1955, echecs: 417 },
          { code: 'demographique', requetes: 0, echecs: 0 },
          { code: 'combinee', requetes: 0, echecs: 0 },
          { code: 'sans_mode', requetes: 230, echecs: 230 },
          { code: 'non_classe', requetes: 0, echecs: 0 },
        ],
      },
    }),
  );
  await page.route('**/api/v1/authentifications/causes*', (route) =>
    route.fulfill({
      json: new URL(route.request().url()).searchParams.get('perimetre') === 'paquets'
        ? {
            perimetre: 'paquets',
            echecs: 144898,
            motifs: [
              { code: 'BIO_NON_CONCORDANTE', libelle: 'Biométrie non concordante', echecs: 106076 },
              { code: 'BIO_ABSENTE', libelle: "Biométrie absente du dossier d'authentification", echecs: 21151 },
              { code: 'NIU_ABSENT', libelle: "NIU absent de la base d'authentification", echecs: 17637 },
              { code: 'MODALITE_VERROUILLEE', libelle: 'Modalité verrouillée par le résident', echecs: 34 },
            ],
          }
        : {
            perimetre: 'usagers',
            echecs: 648,
            motifs: [
              { code: 'OTP_REFUSE', libelle: 'Code OTP ou eKYC refusé', echecs: 417 },
              { code: 'SANS_MODE', libelle: "Aucun mode d'authentification demandé", echecs: 230 },
              { code: 'AUTRE', libelle: 'Motif non répertorié', echecs: 1 },
            ],
          },
    }),
  );
  await page.route('**/api/v1/authentifications/partenaires*', (route) =>
    route.fulfill({
      json: {
        partenairesRaccordes: 1,
        appelants: [
          {
            canal: 'partenaire',
            nom: 'Atos',
            requetes: 1645,
            reussies: 1142,
            demandesOtp: 2159,
            derniereRequete: '2026-01-14',
          },
          {
            canal: 'portail',
            nom: 'Portail du résident',
            requetes: 517,
            reussies: 377,
            demandesOtp: 560,
            derniereRequete: '2026-01-14',
          },
          { canal: 'ussd', nom: 'USSD', requetes: 24, reussies: 19, demandesOtp: 13, derniereRequete: '2026-01-12' },
        ],
      },
    }),
  );
  await page.route('**/api/v1/authentifications/semaines*', (route) =>
    route.fulfill({
      json: {
        semaines: Array.from({ length: 12 }, (_, i) => {
          const lundi = new Date(Date.UTC(2025, 9, 20 + 7 * i)).toISOString().slice(0, 10);
          return { lundi, dansPeriode: true, reussies: 360 + 5 * i, echouees: 150 + 2 * i };
        }),
      },
    }),
  );
  await page.route('**/api/v1/authentifications/paquets*', (route) =>
    route.fulfill({
      json: { disponible: true, verifications: 170151, reussies: 25253, echouees: 144898, autresStatuts: 0 },
    }),
  );
}
