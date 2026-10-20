import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createMemoryHistory } from '@tanstack/react-router';
import { render } from '@testing-library/react';
import { vi } from 'vitest';
import type {
  AgeSexe,
  InscriptionsParSemaine,
  LigneZone,
  Preinscriptions,
  Region,
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
});

const totaux = (lignes: LigneZone[]) => ({
  inscriptions: lignes.reduce((s, l) => s + l.inscriptions, 0),
  niuGeneres: lignes.reduce((s, l) => s + l.niuGeneres, 0),
  enCours: lignes.reduce((s, l) => s + l.enCours, 0),
  echouees: lignes.reduce((s, l) => s + l.echouees, 0),
  rejetees: lignes.reduce((s, l) => s + l.rejetees, 0),
  nonClassees: 0,
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
  ...totaux(LIGNES_SAVANES),
  lignes: LIGNES_SAVANES,
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
export const AGE_SEXE: AgeSexe = {
  perimetre: 'Ensemble du Togo',
  disponible: true,
  nonRenseignes: 0,
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

type Reponse = unknown | ((url: URL) => unknown);

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
  },
  '/enrolement/semaines': SEMAINES,
  '/enrolement/territoire': (url: URL) =>
    url.searchParams.get('zone') === 'SAV' ? TERRITOIRE_SAVANES : TERRITOIRE_NATIONAL,
  '/enrolement/centres': (url: URL) => CENTRES[url.searchParams.get('classement') ?? 'inscriptions'],
  '/enrolement/preinscriptions': PREINSCRIPTIONS,
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
    vi.fn(async (url: URL) => {
      appels.push(url);
      const reponse = toutes[url.pathname.replace(/^.*\/api\/v1/, '')];
      if (reponse === undefined) return new Response('', { status: 404 });
      const corps = typeof reponse === 'function' ? reponse(url) : reponse;
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
