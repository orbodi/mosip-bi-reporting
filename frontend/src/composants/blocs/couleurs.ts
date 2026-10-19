/**
 * Couleurs des séries et des parts (barres de répartition, légendes, graphiques), toutes issues des jetons de
 * styles/jetons.css. Le CSS utilise la classe « couleur--<nom> », ECharts la valeur du jeton.
 */
export const JETON_COULEUR = {
  bleu: '--bleu',
  'serie-1': '--serie-1',
  'bleu-clair': '--seq-2',
  'bleu-pale': '--seq-1',
  'bleu-fonce': '--seq-4',
  or: '--or',
  'en-cours': '--statut-en-cours',
  orange: '--statut-echoue',
  rouge: '--danger',
  'rouge-fonce': '--rouge-fonce',
  vert: '--serie-3',
  gris: '--trait',
} as const;

export type Couleur = keyof typeof JETON_COULEUR;

export const classeCouleur = (c: Couleur) => `couleur--${c}`;
