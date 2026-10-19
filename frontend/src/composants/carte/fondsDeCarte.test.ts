import { describe, expect, it } from 'vitest';
import { CARTE_REGIONS, carteRegion, contourDe } from './fondsDeCarte';

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

  it('retrouve un contour quel que soit l’accent ou la casse', () => {
    const plateaux = carteRegion('Plateaux');
    expect(plateaux && contourDe(plateaux, 'KPELE')?.nom).toBe('Kpélé');
    expect(contourDe(CARTE_REGIONS, 'grand lome')?.nom).toBe('Grand Lomé');
  });
});
