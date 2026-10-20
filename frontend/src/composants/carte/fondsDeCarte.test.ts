import { describe, expect, it } from 'vitest';
import { CARTE_REGIONS, cadrage, carteRegion, contourDe } from './fondsDeCarte';

describe('fonds de carte', () => {
  it('nomme chaque région dans le SVG, du nord au sud', () => {
    expect(CARTE_REGIONS.contours.map((c) => c.nom)).toEqual([
      'Savanes',
      'Kara',
      'Centrale',
      'Plateaux',
      'Maritime',
      'Grand Lomé',
    ]);
    expect(CARTE_REGIONS.svg).toContain('<path name="Grand Lomé"');
  });

  it('cadre une région sur ses préfectures', () => {
    const savanes = carteRegion('Savanes');
    expect(savanes?.contours.map((c) => c.nom)).toEqual([
      'Cinkassé',
      'Tône',
      'Kpendjal',
      'Tandjouaré',
      'Oti',
    ]);
    expect(savanes?.svg).toMatch(/viewBox="-4 -4 /);
    expect(carteRegion('Hors référentiel')).toBeUndefined();
  });

  it('garde les proportions du Togo au lieu de l’étirer sur toute la largeur', () => {
    // 440 px de haut, comme la maquette : la carte occupe 92,9 % de la hauteur, centrée.
    const c = cadrage(CARTE_REGIONS, 600, 440);
    expect(c.height).toBeCloseTo(408.8, 0);
    expect(c.width! / c.height).toBeCloseTo(200 / 523.8, 2);
    expect(c.left).toBeCloseTo((600 - c.width!) / 2, 0);
    expect(c.top).toBeCloseTo(6.2, 0);
    // Cadre étroit : la largeur limite, la hauteur suit les proportions.
    const savanes = carteRegion('Savanes')!;
    const etroit = cadrage(savanes, 150, 380);
    expect(etroit.width).toBeCloseTo(150 * 0.88, 0);
    expect(etroit.width! / etroit.height).toBeCloseTo(savanes.largeur / savanes.hauteur, 2);
    // Avant la mesure du cadre : hauteur fixée, ECharts centre et calcule la largeur.
    const avant = cadrage(CARTE_REGIONS, 0, 440);
    expect(avant.left).toBe('center');
    expect(avant.width).toBeUndefined();
    expect(avant.height).toBeCloseTo(408.8, 0);
  });

  it('retrouve un contour quel que soit l’accent ou la casse', () => {
    const plateaux = carteRegion('Plateaux');
    expect(plateaux && contourDe(plateaux, 'KPELE')?.nom).toBe('Kpélé');
    expect(contourDe(CARTE_REGIONS, 'grand lome')?.nom).toBe('Grand Lomé');
  });
});
