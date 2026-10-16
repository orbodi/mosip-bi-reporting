import { describe, expect, it } from 'vitest';
import { dateFr, heureFr, miseAJourFr, nf, part, pct } from './format';

describe('nf', () => {
  it('sépare les milliers par une espace fine insécable', () => {
    expect(nf(3278239)).toBe('3\u202f278\u202f239');
    expect(nf(14)).toBe('14');
  });
  it('affiche un tiret pour une valeur non calculable', () => {
    expect(nf(Number.NaN)).toBe('–');
  });
});

describe('pct', () => {
  it('affiche une décimale et une espace insécable avant %', () => {
    expect(pct(1770796 / 3278239)).toBe('54,0\u00a0%');
    expect(pct(0.577)).toBe('57,7\u00a0%');
  });
  it('affiche un tiret quand le dénominateur est nul', () => {
    expect(pct(part(3, 0))).toBe('–');
  });
});

describe('dates', () => {
  it('formate à l’heure du Togo', () => {
    expect(dateFr('2026-01-14T11:59:00Z')).toBe('14/01/2026');
    expect(heureFr('2026-01-14T11:59:00Z')).toBe('11h59');
    expect(miseAJourFr('2026-07-03T17:09:00Z')).toBe('03/07/2026 à 17h09');
  });
});
