import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';
import { simulerEnrolement } from './api';

const META = {
  application: 'BI Reporting ANID',
  sources: [
    {
      source: 'enrolement',
      libelle: 'Enrôlement',
      premiereDonnee: '2024-01-01',
      derniereDonnee: '2026-01-14T11:42:00Z',
    },
    {
      source: 'cartes',
      libelle: 'Impression des cartes',
      premiereDonnee: '2024-02-01',
      derniereDonnee: '2026-01-14T11:59:00Z',
    },
    { source: 'abis', libelle: 'ABIS', premiereDonnee: '2024-01-01', derniereDonnee: '2026-07-13T11:59:00Z' },
    { source: 'idps', libelle: 'IDPS', premiereDonnee: '2026-07-03', derniereDonnee: '2026-07-03T17:09:00Z' },
    {
      source: 'authentifications',
      libelle: 'Authentifications',
      premiereDonnee: '2025-02-01',
      derniereDonnee: '2026-01-14T11:05:00Z',
    },
  ],
};

test.beforeEach(async ({ page }) => {
  await page.route('**/api/v1/meta', (route) => route.fulfill({ json: META }));
  await page.route('**/api/v1/enrolement/devenir*', (route) =>
    route.fulfill({
      json: {
        perimetre: 'Ensemble du Togo',
        inscriptions: 3278239,
        niuGeneres: 3058886,
        enCours: 123639,
        echouees: 9218,
        rejetees: 86496,
        nonClassees: 0,
      },
    }),
  );
  await simulerEnrolement(page);
});

/** Les sept pages de la maquette : titre, premier bloc, accessibilité et capture (skill /verif-visuelle). */
const PAGES = [
  {
    chemin: '/',
    titre: 'Vue d’ensemble du parcours citoyen',
    bloc: 'De la pré-inscription à la carte en main',
    maquette: 'Main',
  },
  { chemin: '/enrolement', titre: 'Enrôlement', bloc: 'Pré-inscription', maquette: 'Enrolement' },
  {
    chemin: '/impression-cartes',
    titre: 'Impression des cartes',
    bloc: 'Impression et remise',
    maquette: 'Cartes',
  },
  { chemin: '/abis', titre: 'ABIS', bloc: 'Transactions ABIS', maquette: 'Biometrie' },
  { chemin: '/idps', titre: 'IDPS', bloc: 'Ordres d’impression', maquette: 'Idps' },
  {
    chemin: '/authentifications',
    titre: 'Authentifications',
    bloc: 'Requêtes d’authentification',
    maquette: 'Usage',
  },
  {
    chemin: '/exploration',
    titre: 'Exploration des données',
    bloc: 'Inscriptions par région',
    maquette: 'Technique',
  },
];

for (const p of PAGES) {
  test(`${p.titre} : mise en page de la maquette, accessibilité et capture`, async ({ page }, testInfo) => {
    await page.goto(p.chemin);
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(p.titre);
    await expect(page.getByRole('heading', { level: 2, name: p.bloc })).toBeVisible();

    const audit = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
    expect(audit.violations.map((v) => `${v.id} : ${v.help} (${v.nodes.length})`)).toEqual([]);

    // À comparer à maquette/captures/<maquette>-*.png.
    await testInfo.attach(`${p.maquette}-${testInfo.project.name}`, {
      body: await page.screenshot({ fullPage: true }),
      contentType: 'image/png',
    });
  });
}

test('Vue d’ensemble : les étapes d’enrôlement viennent de l’API, les autres restent « – »', async ({
  page,
}) => {
  await page.goto('/');
  const parcours = page.getByRole('region', { name: 'De la pré-inscription à la carte en main' });
  await expect(parcours.getByText('3 278 239')).toBeVisible();
  await expect(parcours.getByText('3 058 886')).toBeVisible();
  await expect(page.getByRole('link', { name: /Impression des cartes.*cartes remises/ })).toBeVisible();
});

test('Exploration : ventilation par préfecture d’une région et export CSV', async ({ page }) => {
  await page.goto('/exploration');
  const resultat = page.getByRole('region', { name: 'Inscriptions par région' });
  await resultat.getByRole('button', { name: /Kara/ }).click();
  await expect(page.getByRole('heading', { level: 2, name: 'Inscriptions par préfecture' })).toBeVisible();
  await expect(page.getByRole('cell', { name: '132 000' })).toBeVisible();
  const [telechargement] = await Promise.all([
    page.waitForEvent('download'),
    page.getByRole('button', { name: 'Exporter en CSV' }).click(),
  ]);
  expect(telechargement.suggestedFilename()).toBe('exploration-enrol-pref.csv');
});
