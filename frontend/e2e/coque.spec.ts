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
      dernierChargement: '2026-01-14T12:05:00Z',
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

const DEVENIR = {
  perimetre: 'Ensemble du Togo',
  inscriptions: 3278239,
  niuGeneres: 3058886,
  enCours: 123639,
  echouees: 9218,
  rejetees: 86496,
  nonClassees: 0,
};

test.beforeEach(async ({ page }) => {
  await page.route('**/api/v1/meta', (route) => route.fulfill({ json: META }));
  await page.route('**/api/v1/enrolement/devenir*', (route) => route.fulfill({ json: DEVENIR }));
  await simulerEnrolement(page);
});

test('Vue d’ensemble : titre, date de mise à jour et accessibilité', async ({ page }, testInfo) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Vue d’ensemble du parcours citoyen');
  await expect(page.getByText('Dernière mise à jour : 14/01/2026 à 12h05')).toBeVisible();

  const audit = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();
  expect(audit.violations.map((v) => `${v.id} : ${v.help}`)).toEqual([]);

  // Capture jointe au rapport, à comparer à maquette/captures/Main-*.png (skill /verif-visuelle).
  await testInfo.attach(`vue-ensemble-${testInfo.project.name}`, {
    body: await page.screenshot({ fullPage: true }),
    contentType: 'image/png',
  });
});

test('Navigation entre les pages', async ({ page, isMobile }) => {
  await page.goto('/');
  if (isMobile) await page.getByText('Menu').click();
  const nav = page.getByRole('navigation', { name: 'Sections du tableau de bord' }).locator('visible=true');
  await nav.getByRole('link', { name: 'Authentifications' }).click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Authentifications');
  await expect(nav.getByRole('link', { name: 'Authentifications' })).toHaveAttribute('aria-current', 'page');
});

test('Enrôlement : devenir des inscriptions, accessibilité et capture', async ({ page }, testInfo) => {
  await page.goto('/enrolement');
  const bloc = page.getByRole('region', { name: 'Devenir des inscriptions' });
  await expect(bloc.getByText('NIU générés, soit 93,3', { exact: false })).toBeVisible();
  await expect(bloc.getByRole('img', { name: /NIU générés 93,3/ })).toBeVisible();
  await expect(bloc.getByText('Actualisé automatiquement toutes les 30 secondes.')).toBeVisible();

  const audit = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();
  expect(audit.violations.map((v) => `${v.id} : ${v.help}`)).toEqual([]);

  // À comparer à maquette/captures/Enrolement-*.png (skill /verif-visuelle).
  await testInfo.attach(`enrolement-${testInfo.project.name}`, {
    body: await page.screenshot({ fullPage: true }),
    contentType: 'image/png',
  });
});

test('Enrôlement : sans filtres ; une région ouverte dans le Territoire, le reste de la page national', async ({
  page,
}) => {
  await page.goto('/enrolement');
  await expect(page.getByRole('link', { name: /Filtres détaillés dans l’Exploration/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /^Période/ })).toHaveCount(0);
  await expect(page.getByRole('button', { name: /^Région/ })).toHaveCount(0);
  await expect(page.getByRole('heading', { name: 'Territoire : vue nationale' })).toBeVisible();
  const territoire = page.getByRole('region', { name: /^Territoire/ });
  await expect(territoire.getByText('▲', { exact: false }).first()).toBeVisible();

  await territoire.getByRole('table', { name: 'Régions' }).getByRole('button', { name: /Kara/ }).click();
  await expect(page).toHaveURL(/region=KAR/);
  await expect(page.getByRole('heading', { name: 'Territoire : région Kara' })).toBeVisible();
  await expect(territoire.getByRole('table', { name: 'Préfectures de la région Kara' })).toBeVisible();
  // Seul le bloc Territoire suit la région : le top des centres reste national.
  await expect(
    page.getByRole('region', { name: 'Top des centres' }).getByText('Ensemble du Togo').first(),
  ).toBeVisible();

  await territoire.getByRole('button', { name: 'Togo' }).click();
  await expect(page.getByRole('heading', { name: 'Territoire : vue nationale' })).toBeVisible();

  const audit = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();
  expect(audit.violations.map((v) => `${v.id} : ${v.help}`)).toEqual([]);
});

test('Enrôlement : onglets du top des centres au clavier', async ({ page }) => {
  await page.goto('/enrolement');
  const top = page.getByRole('region', { name: 'Top des centres' });
  await expect(top.getByText('EPP Doumassesse I G/B')).toBeVisible();
  await top.getByRole('tab', { name: 'Plus d’enregistrements' }).focus();
  await page.keyboard.press('ArrowRight');
  await expect(top.getByRole('tab', { name: 'Plus d’échecs' })).toHaveAttribute('aria-selected', 'true');
  await expect(top.getByRole('columnheader', { name: 'Échecs' })).toBeVisible();
  await expect(top.getByText('EPP Worgou G/A')).toBeVisible();
});
