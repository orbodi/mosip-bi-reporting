// Captures pleine page d'une route aux trois largeurs de référence de la maquette.
// Usage : node e2e/outils/captures.mjs /enrolement   (front lancé avec « npm run dev »)
// Sortie : test-results/captures/<page>-<largeur>.png
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from '@playwright/test';

const chemin = process.argv[2] ?? '/';
const base = process.env.CAPTURE_URL ?? 'http://localhost:5173';
const dossier = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  '..',
  '..',
  'test-results',
  'captures',
);
const nom = chemin === '/' ? 'vue-ensemble' : chemin.replace(/^\//, '').replace(/[/?&=]/g, '-');
const LARGEURS = [1440, 1000, 390];

// Méta de secours si l'API ne répond pas (dates du BI actuel).
const META_SECOURS = {
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

mkdirSync(dossier, { recursive: true });
const navigateur = await chromium.launch();
try {
  for (const largeur of LARGEURS) {
    const page = await navigateur.newPage({
      viewport: { width: largeur, height: 900 },
      locale: 'fr-FR',
      timezoneId: 'Africa/Lome',
    });
    await page.route('**/api/v1/meta', async (route) => {
      try {
        const reponse = await route.fetch();
        if (reponse.ok()) return route.fulfill({ response: reponse });
      } catch {
        // API arrêtée : on simule ci-dessous.
      }
      if (largeur === LARGEURS[0]) console.warn('API indisponible : méta simulée.');
      return route.fulfill({ json: META_SECOURS });
    });
    await page.goto(`${base}${chemin}`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(300);
    const fichier = path.join(dossier, `${nom}-${largeur}.png`);
    await page.screenshot({ path: fichier, fullPage: true });
    console.log(fichier);
  }
} finally {
  await navigateur.close();
}
