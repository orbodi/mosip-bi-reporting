/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // En développement, l'API Spring Boot tourne sur 8080 (profil dev) ; API_PROXY_CIBLE la désigne quand le front
    // tourne dans Docker (deploy/docker-compose.yml, profil temps-reel).
    proxy: { '/api': process.env.API_PROXY_CIBLE ?? 'http://localhost:8080' },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    css: false,
    // Sur le serveur, la suite tourne à côté du front en service : 5 s ne suffisent pas toujours (25/10/2026).
    testTimeout: 15_000,
  },
});
