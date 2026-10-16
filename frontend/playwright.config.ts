import { defineConfig, devices } from '@playwright/test';

/**
 * Parcours de bout en bout sur le build de production (vite preview), API simulée dans chaque test.
 * Trois largeurs de référence de la maquette : 1 440, 1 000 et 390 px.
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: 'http://localhost:4173',
    locale: 'fr-FR',
    timezoneId: 'Africa/Lome',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'bureau-1440', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } } },
    { name: 'tablette-1000', use: { ...devices['Desktop Chrome'], viewport: { width: 1000, height: 800 } } },
    { name: 'mobile-390', use: { ...devices['Pixel 7'], viewport: { width: 390, height: 844 } } },
  ],
  webServer: {
    command: 'npm run build && npm run preview',
    url: 'http://localhost:4173',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
