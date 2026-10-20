import { describe, expect, it } from 'vitest';
import { dateFr, heureFr, jourMoisCourt, jourMoisFr, miseAJourFr, nf, part, pct } from './format';

describe('nf', () => {
  it('sépare les milliers par une espace fine insécable', () => {
    expect(nf(3278239)).toBe('3\u202f278\u202f239');
    expect(nf(14)).toBe('14');
  });
  it('affiche 0 pour une valeur indisponible', () => {
    expect(nf(Number.NaN)).toBe('0');
  });
});

describe('pct', () => {
  it('affiche une décimale et une espace insécable avant %', () => {
    expect(pct(1770796 / 3278239)).toBe('54,0\u00a0%');
    expect(pct(0.577)).toBe('57,7\u00a0%');
  });
  it('affiche 0,0 % quand le dénominateur est nul', () => {
    expect(pct(part(3, 0))).toBe('0,0\u00a0%');
  });
});

describe('dates', () => {
  it('formate à l’heure du Togo', () => {
    expect(dateFr('2026-01-14T11:59:00Z')).toBe('14/01/2026');
    expect(heureFr('2026-01-14T11:59:00Z')).toBe('11h59');
    expect(miseAJourFr('2026-07-03T17:09:00Z')).toBe('03/07/2026 à 17h09');
  });
});

describe('jours d’une semaine', () => {
  it('écrit le jour et le mois en toutes lettres ou en chiffres', () => {
    expect(jourMoisFr('2026-01-05')).toBe('5 janvier');
    expect(jourMoisFr('2025-12-29')).toBe('29 décembre');
    expect(jourMoisCourt('2026-01-05')).toBe('05/01');
  });
});
