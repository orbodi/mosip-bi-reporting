import { describe, expect, it } from 'vitest';
import {
  datesPersonnalisees,
  erreurPersonnalisee,
  estPersonnalisee,
  libellePersonnalisee,
  periodePersonnalisee,
  plageExploration,
} from './periodeExploration';

const BORNES = { du: '2024-01-01', au: '2026-11-05' };

describe('Période de l’Exploration', () => {
  it('années et mois : du premier au dernier jour', () => {
    expect(plageExploration('A:2025')).toEqual({ du: '2025-01-01', au: '2025-12-31' });
    expect(plageExploration('M:2026-02')).toEqual({ du: '2026-02-01', au: '2026-02-28' });
    expect(plageExploration('tout')).toBeUndefined();
  });

  it('personnalisée : un jour précis si la fin est vide, sinon l’intervalle, bornes comprises', () => {
    const jour = periodePersonnalisee('2026-10-02', '');
    expect(estPersonnalisee(jour)).toBe(true);
    expect(datesPersonnalisees(jour)).toEqual({ du: '2026-10-02', au: '' });
    expect(plageExploration(jour, BORNES)).toEqual({ du: '2026-10-02', au: '2026-10-02' });
    expect(libellePersonnalisee(jour)).toBe('le 02/10/2026');

    const intervalle = periodePersonnalisee('2026-10-02', '2026-10-15');
    expect(plageExploration(intervalle, BORNES)).toEqual({ du: '2026-10-02', au: '2026-10-15' });
    expect(libellePersonnalisee(intervalle)).toBe('du 02/10/2026 au 15/10/2026');
    expect(erreurPersonnalisee(intervalle, BORNES)).toBeUndefined();
  });

  it('personnalisée invalide : message et aucun calcul', () => {
    expect(erreurPersonnalisee(periodePersonnalisee('', ''), BORNES)).toBe('Choisissez au moins la date de début.');
    const inverse = periodePersonnalisee('2026-10-15', '2026-10-02');
    expect(erreurPersonnalisee(inverse, BORNES)).toBe('La date de fin doit suivre la date de début.');
    expect(plageExploration(inverse, BORNES)).toBeUndefined();
    expect(erreurPersonnalisee(periodePersonnalisee('2023-05-01', '2023-05-31'), BORNES)).toBe(
      'Aucune donnée sur cette période : données du 01/01/2024 au 05/11/2026.',
    );
    expect(libellePersonnalisee(periodePersonnalisee('', ''))).toBe('Période personnalisée');
  });
});
