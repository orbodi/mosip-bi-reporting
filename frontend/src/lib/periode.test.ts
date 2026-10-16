import { describe, expect, it } from 'vitest';
import { plagePeriode } from './periode';

const enrolement = { du: '2024-01-01', au: '2026-01-14' };

describe('plagePeriode', () => {
  it('« Depuis le début » couvre toutes les données', () => {
    expect(plagePeriode('tout', enrolement)).toEqual(enrolement);
  });

  it('les 7 derniers jours finissent à la dernière donnée (exemple de la maquette)', () => {
    expect(plagePeriode('7j', enrolement)).toEqual({ du: '2026-01-08', au: '2026-01-14' });
  });

  it('ne remonte pas avant la première donnée', () => {
    expect(plagePeriode('90j', { du: '2026-01-01', au: '2026-01-14' })).toEqual({
      du: '2026-01-01',
      au: '2026-01-14',
    });
  });

  it('borne et remet dans l’ordre une période personnalisée', () => {
    expect(plagePeriode('perso', enrolement, { du: '2026-03-01', au: '2023-05-01' })).toEqual({
      du: '2024-01-01',
      au: '2026-01-14',
    });
    expect(plagePeriode('perso', enrolement, { du: '2025-06-01' })).toEqual({
      du: '2025-06-01',
      au: '2026-01-14',
    });
  });
});
