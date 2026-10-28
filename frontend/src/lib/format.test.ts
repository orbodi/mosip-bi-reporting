import { describe, expect, it } from 'vitest';
import {
  dateFr,
  heureFr,
  jourMoisCourt,
  jourMoisFr,
  miseAJourFr,
  nf,
  part,
  pct,
  dimanche,
  etiquetteVisible,
  semaineCourte,
  semaineDates,
  semaineFr,
  typographie,
} from './format';

describe('nf', () => {
  it('sépare les milliers par une espace fine insécable', () => {
    expect(nf(3278239)).toBe('3\u202f278\u202f239');
    expect(nf(14)).toBe('14');
  });
  it('affiche 0 pour une valeur indisponible', () => {
    expect(nf(Number.NaN)).toBe('0');
  });
});

describe('typographie', () => {
  it('met une espace insécable avant ; : ! ? et dans les guillemets', () => {
    expect(typographie('Doublon possible : un vérificateur doit trancher ; vite ?')).toBe(
      'Doublon possible\u00a0: un vérificateur doit trancher\u00a0; vite\u00a0?',
    );
    expect(typographie('le « motif »')).toBe('le «\u00a0motif\u00a0»');
    expect(typographie('Sans ponctuation')).toBe('Sans ponctuation');
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

  it('écrit une semaine du lundi au dimanche', () => {
    expect(dimanche('2026-10-19')).toBe('2026-10-25');
    expect(semaineCourte('2026-10-19')).toBe('19\u201325/10');
    expect(semaineCourte('2026-09-28')).toBe('28/09\u201304/10');
    expect(semaineCourte('2025-12-29')).toBe('29/12\u201304/01');
    expect(semaineFr('2026-10-19')).toBe('du 19 au 25 octobre');
    expect(semaineFr('2026-09-28')).toBe('du 28 septembre au 4 octobre');
    expect(semaineFr('2026-01-05')).toBe('du 5 au 11 janvier');
    expect(semaineDates('2026-10-19')).toBe('19/10/2026 au 25/10/2026');
  });

  it('garde toujours visible l’étiquette de la dernière semaine', () => {
    const visible = etiquetteVisible(12, 2);
    expect([0, 1, 9, 10, 11].map(visible)).toEqual([false, true, true, false, true]);
    expect(etiquetteVisible(12, 1)(0)).toBe(true);
  });
});
