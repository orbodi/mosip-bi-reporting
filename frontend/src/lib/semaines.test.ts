import { describe, expect, it } from 'vitest';
import { lectureSemaine } from './semaines';

const SEMAINE = { lundi: '2026-01-05', dansLaPeriode: true, inscriptions: 20230, niuGeneres: 17626 };

describe('lectureSemaine', () => {
  it('reprend la phrase de la maquette, nombre d’abord puis pourcentage', () => {
    expect(lectureSemaine(SEMAINE)).toBe(
      'Semaine du 5 au 11 janvier : 20 230 inscriptions, 17 626 NIU générés (87,1 %).',
    );
  });

  it('affiche 0 pour des chiffres indisponibles', () => {
    expect(lectureSemaine({ ...SEMAINE, inscriptions: Number.NaN, niuGeneres: Number.NaN })).toBe(
      'Semaine du 5 au 11 janvier : 0 inscriptions, 0 NIU générés (0,0 %).',
    );
  });
});
