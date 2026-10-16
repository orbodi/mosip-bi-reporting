// Stop : avant que Claude rende la main, lance les vérifications des parties modifiées.
// Code de sortie 2 = Claude reprend la main avec le message d'échec pour corriger.
import { existsSync } from 'node:fs';
import path from 'node:path';
import { RACINE, fin, lancer, lireEvenement } from './commun.mjs';

const evenement = lireEvenement();
// Déjà relancé par ce hook : ne pas boucler.
if (evenement.stop_hook_active) process.exit(0);

function partiesModifiees() {
  const statut = lancer('git status --porcelain', RACINE, 15_000);
  if (!statut.ok) return new Set(['frontend', 'backend']); // pas de dépôt git : tout vérifier
  const parties = new Set();
  for (const ligne of statut.sortie.split('\n')) {
    const chemin = ligne.slice(3).trim();
    if (chemin.startsWith('frontend/')) parties.add('frontend');
    if (chemin.startsWith('backend/')) parties.add('backend');
  }
  return parties;
}

const parties = partiesModifiees();
const echecs = [];

if (parties.has('frontend') && existsSync(path.join(RACINE, 'frontend', 'node_modules'))) {
  const dossier = path.join(RACINE, 'frontend');
  for (const commande of ['npm run -s lint', 'npm run -s typecheck', 'npm test --silent']) {
    const r = lancer(commande, dossier, 300_000);
    if (!r.ok) {
      echecs.push(`frontend : « ${commande} » a échoué\n${fin(r.sortie)}`);
      break;
    }
  }
}

if (parties.has('backend')) {
  const r = lancer('mvn -q -B test', path.join(RACINE, 'backend'), 600_000);
  if (r.introuvable) {
    process.stderr.write('Maven introuvable : tests backend non lancés.\n');
  } else if (!r.ok) {
    echecs.push(`backend : « mvn test » a échoué\n${fin(r.sortie)}`);
  }
}

if (echecs.length > 0) {
  process.stderr.write(`Vérifications en échec, corriger avant de terminer :\n\n${echecs.join('\n\n')}\n`);
  process.exit(2);
}
process.exit(0);
