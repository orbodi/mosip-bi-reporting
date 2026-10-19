import { cleNom } from '../../lib/territoire';
import {
  CONTOURS_PREFECTURES,
  CONTOURS_REGIONS,
  HAUTEUR_CARTE,
  LARGEUR_CARTE,
  type Contour,
} from './contoursTogo';

/** Fond de carte SVG pour ECharts (registerMap) : chaque contour est un chemin nommé. */
export interface FondDeCarte {
  /** Nom d'enregistrement dans ECharts. */
  nom: string;
  svg: string;
  contours: readonly Contour[];
}

const MARGE = 4;

const echapper = (texte: string) =>
  texte.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');

function svg(contours: readonly Contour[], boite: readonly number[]): string {
  const chemins = contours.map((c) => `<path name="${echapper(c.nom)}" d="${c.d}"/>`).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${boite.join(' ')}">${chemins}</svg>`;
}

/** Les six régions du Togo. */
export const CARTE_REGIONS: FondDeCarte = {
  nom: 'togo-regions',
  svg: svg(CONTOURS_REGIONS, [0, 0, LARGEUR_CARTE, HAUTEUR_CARTE]),
  contours: CONTOURS_REGIONS,
};

/** Les préfectures d'une région, cadrées sur la région ; undefined si aucun contour ne porte ce nom de région. */
export function carteRegion(nomRegion: string): FondDeCarte | undefined {
  const cle = cleNom(nomRegion);
  const contours = CONTOURS_PREFECTURES.filter((p) => cleNom(p.region ?? '') === cle);
  if (contours.length === 0) return undefined;
  const x0 = Math.min(...contours.map((c) => c.boite[0])) - MARGE;
  const y0 = Math.min(...contours.map((c) => c.boite[1])) - MARGE;
  const x1 = Math.max(...contours.map((c) => c.boite[0] + c.boite[2])) + MARGE;
  const y1 = Math.max(...contours.map((c) => c.boite[1] + c.boite[3])) + MARGE;
  return { nom: `togo-${cle}`, svg: svg(contours, [x0, y0, x1 - x0, y1 - y0]), contours };
}

/** Contour qui porte ce nom de zone (comparaison sans accents ni casse), s'il existe. */
export function contourDe(fond: FondDeCarte, nomZone: string): Contour | undefined {
  const cle = cleNom(nomZone);
  return fond.contours.find((c) => cleNom(c.nom) === cle);
}
