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
  /** Taille de la boîte du SVG (unités des contours) : son rapport largeur / hauteur doit être gardé à l'écran. */
  largeur: number;
  hauteur: number;
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
  largeur: LARGEUR_CARTE,
  hauteur: HAUTEUR_CARTE,
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
  return {
    nom: `togo-${cle}`,
    svg: svg(contours, [x0, y0, x1 - x0, y1 - y0]),
    contours,
    largeur: x1 - x0,
    hauteur: y1 - y0,
  };
}

/** Place de la carte dans son cadre, en pixels (options left, top, width, height d'ECharts). */
export interface Cadrage {
  left: number | 'center';
  top: number;
  width?: number;
  height: number;
}

/**
 * Cadrage de la maquette : la carte garde ses proportions (le Togo est étroit et haut), centrée, avec une marge de
 * 6 % de chaque côté, 1,4 % en haut et 5,7 % en bas (place de l'étiquette « Grand Lomé »). ECharts étire la carte
 * dès que left, right, top et bottom sont tous donnés : on calcule donc la boîte ici. Sans largeur mesurée (premier
 * rendu), la carte prend la hauteur et ECharts la centre.
 */
export function cadrage(fond: FondDeCarte, largeur: number, hauteur: number): Cadrage {
  const haut = hauteur * 0.014;
  const dispoH = hauteur * (1 - 0.014 - 0.057);
  if (!(largeur > 0)) return { left: 'center', top: haut, height: dispoH };
  const dispoL = largeur * (1 - 2 * 0.06);
  const echelle = Math.min(dispoL / fond.largeur, dispoH / fond.hauteur);
  const l = fond.largeur * echelle;
  const h = fond.hauteur * echelle;
  return {
    left: Math.round(((largeur - l) / 2) * 10) / 10,
    top: Math.round((haut + (dispoH - h) / 2) * 10) / 10,
    width: Math.round(l * 10) / 10,
    height: Math.round(h * 10) / 10,
  };
}

/** Contour qui porte ce nom de zone (comparaison sans accents ni casse), s'il existe. */
export function contourDe(fond: FondDeCarte, nomZone: string): Contour | undefined {
  const cle = cleNom(nomZone);
  return fond.contours.find((c) => cleNom(c.nom) === cle);
}
