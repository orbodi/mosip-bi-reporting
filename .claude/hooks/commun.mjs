// Outils communs aux hooks Claude Code du projet (Node, sans dépendance).
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import path from 'node:path';

export const RACINE = process.env.CLAUDE_PROJECT_DIR || process.cwd();

/** Lit l'événement JSON envoyé par Claude Code sur l'entrée standard. */
export function lireEvenement() {
  try {
    return JSON.parse(readFileSync(0, 'utf8') || '{}');
  } catch {
    return {};
  }
}

/** Chemin relatif à la racine du dépôt, avec des « / ». */
export function relatif(fichier) {
  if (!fichier) return '';
  return path.relative(RACINE, path.resolve(RACINE, fichier)).split(path.sep).join('/');
}

/** Lance une commande et renvoie { ok, sortie } ; shell pour trouver npm/mvn aussi sous Windows. */
export function lancer(commande, dossier, delaiMs = 600_000) {
  const r = spawnSync(commande, { cwd: dossier, shell: true, encoding: 'utf8', timeout: delaiMs });
  const sortie = `${r.stdout ?? ''}${r.stderr ?? ''}`;
  return { ok: r.status === 0, introuvable: r.status === 127, sortie };
}

/** Dernières lignes d'une sortie, pour garder le message court. */
export function fin(texte, lignes = 40) {
  return texte.trim().split('\n').slice(-lignes).join('\n');
}
