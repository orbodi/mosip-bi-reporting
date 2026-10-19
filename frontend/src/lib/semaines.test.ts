import { describe, expect, it } from 'vitest';
import { lectureSemaine } from './semaines';

const SEMAINE = { lundi: '2026-01-05', dansLaPeriode: true, inscriptions: 20230, niuGeneres: 17626 };

describe('lectureSemaine', () => {
  it('reprend la phrase de la maquette, nombre d’abord puis pourcentage', () => {
    expect(lectureSemaine(SEMAINE, true)).toBe(
      'Semaine du 5 janvier : 20 230 inscriptions, 17 626 NIU générés (87,1 %).',
    );
  });

  it('tait les NIU tant que leur source n’est pas alimentée', () => {
    expect(lectureSemaine(SEMAINE, false)).toBe('Semaine du 5 janvier : 20 230 inscriptions.');
  });
});
