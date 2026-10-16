// PostToolUse (Edit, Write) : formate le fichier modifié et signale les erreurs de lint à Claude.
// Code de sortie 2 = le message sur stderr est renvoyé à Claude pour correction (le fichier est déjà écrit).
import { existsSync } from 'node:fs';
import path from 'node:path';
import { RACINE, fin, lancer, lireEvenement, relatif } from './commun.mjs';

const fichier = relatif(lireEvenement().tool_input?.file_path);
const FRONT = path.join(RACINE, 'frontend');

if (!fichier.startsWith('frontend/') || !existsSync(path.join(FRONT, 'node_modules'))) process.exit(0);

const local = fichier.slice('frontend/'.length);
if (/\.(ts|tsx|css|json|md|html)$/.test(local) && !local.startsWith('src/api/schema.ts')) {
  lancer(`npx prettier --write --log-level=warn "${local}"`, FRONT, 50_000);
}
if (/\.(ts|tsx)$/.test(local) && !local.startsWith('src/api/schema.ts')) {
  const lint = lancer(`npx eslint --fix "${local}"`, FRONT, 50_000);
  if (!lint.ok) {
    process.stderr.write(`ESLint signale des erreurs dans ${fichier} :\n${fin(lint.sortie, 25)}\n`);
    process.exit(2);
  }
}
process.exit(0);
