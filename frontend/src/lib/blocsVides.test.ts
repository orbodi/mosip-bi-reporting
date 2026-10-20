import { describe, expect, it } from 'vitest';
import { nf, part, pct } from './format';
import {
  devenirInconnu,
  largeurPyramide,
  lundisDesSemainesCompletes,
  pyramideInconnue,
  semainesInconnues,
} from './blocsVides';

describe('données de remplacement', () => {
  it('calcule les 12 semaines complètes comme l’API', () => {
    const lundis = lundisDesSemainesCompletes('2026-01-14');
    expect(lundis).toHaveLength(12);
    expect(lundis[0]).toBe('2025-10-20');
    expect(lundis[11]).toBe('2026-01-05');
    expect(lundisDesSemainesCompletes('2026-01-11')[11]).toBe('2026-01-05');
    expect(lundisDesSemainesCompletes('2026-01-12')[11]).toBe('2026-01-05');
  });

  it('affiche 0 pour les valeurs inconnues', () => {
    const d = devenirInconnu();
    expect(nf(d.inscriptions)).toBe('0');
    expect(pct(part(d.niuGeneres, d.inscriptions))).toBe('0,0\u00a0%');
    expect(semainesInconnues('2026-01-14').semaines.every((s) => Number.isNaN(s.inscriptions))).toBe(true);
  });

  it('pyramide : 8 tranches de la plus âgée à la plus jeune, chiffres à 0 et barres vides', () => {
    const lignes = pyramideInconnue();
    expect(lignes.map((l) => l.tranche)).toEqual([
      '60 ans et +',
      '46 à 60',
      '36 à 45',
      '26 à 35',
      '19 à 25',
      '15 à 18',
      '6 à 14',
      '0 à 5',
    ]);
    expect(lignes.every((l) => nf(l.femmes) === '0' && nf(l.hommes) === '0')).toBe(true);
    expect(lignes.every((l) => largeurPyramide(l.femmes, lignes) === 0)).toBe(true);
  });

  it('pyramide : la plus grande valeur des deux sexes occupe 70 % de la demi-largeur', () => {
    const lignes = [
      { tranche: '19 à 25', femmes: 50, hommes: 100 },
      { tranche: '0 à 5', femmes: 25, hommes: Number.NaN },
    ];
    expect(largeurPyramide(100, lignes)).toBe(70);
    expect(largeurPyramide(50, lignes)).toBe(35);
    expect(largeurPyramide(Number.NaN, lignes)).toBe(0);
  });
});
