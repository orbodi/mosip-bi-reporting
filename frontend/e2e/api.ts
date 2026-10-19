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
  };
};

type Ligne = ReturnType<typeof zone>;

const territoire = (perimetre: string, code: string | null, lignes: Ligne[]) => ({
  perimetre,
  zone: code,
  inscriptions: lignes.reduce((s, l) => s + l.inscriptions, 0),
  niuGeneres: lignes.reduce((s, l) => s + l.niuGeneres, 0),
  enCours: lignes.reduce((s, l) => s + l.enCours, 0),
  echouees: lignes.reduce((s, l) => s + l.echouees, 0),
  rejetees: lignes.reduce((s, l) => s + l.rejetees, 0),
  nonClassees: 0,
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
};

export async function simulerEnrolement(page: Page) {
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
