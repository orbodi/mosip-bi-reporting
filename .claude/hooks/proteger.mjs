// PreToolUse (Edit, Write) : bloque les modifications interdites par les règles du projet.
// Code de sortie 2 = action refusée, le message sur stderr est renvoyé à Claude.
import { existsSync } from 'node:fs';
import path from 'node:path';
import { RACINE, lancer, lireEvenement, relatif } from './commun.mjs';

const evenement = lireEvenement();
const fichier = relatif(evenement.tool_input?.file_path ?? evenement.tool_input?.notebook_path);

function refuser(message) {
  process.stderr.write(`${message}\n`);
  process.exit(2);
}

if (!fichier) process.exit(0);

// 1. Secrets : pas de .env réel (les .env.example restent modifiables).
const nom = path.posix.basename(fichier);
if (/^\.env($|\.)/.test(nom) && !nom.endsWith('.example')) {
  refuser(`Fichier de secrets protégé (${fichier}). Modifier le .env.example correspondant et laisser l'humain remplir le .env.`);
}

// 2. Maquette : référence visuelle validée, en lecture seule.
if (fichier.startsWith('maquette/') && process.env.BI_MAQUETTE_MODIFIABLE !== '1') {
  refuser(`maquette/ est la référence validée par l'ANID et ne se modifie pas (${fichier}). Changer l'application, pas la maquette.`);
}

// 3. Migrations Flyway déjà versionnées : en ajout seulement.
if (/^backend\/src\/main\/resources\/db\/migration\/V[^/]+\.sql$/.test(fichier) && existsSync(path.join(RACINE, fichier))) {
  const suivi = lancer(`git ls-files --error-unmatch "${fichier}"`, RACINE, 10_000);
  if (suivi.ok) {
    refuser(`Migration déjà versionnée (${fichier}) : ne jamais la modifier. Créer une nouvelle migration V<n+1>__description.sql.`);
  }
}

process.exit(0);
