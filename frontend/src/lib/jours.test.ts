import { describe, expect, it } from 'vitest';
import type { InscriptionsParJour } from '../api/client';
import {
  aujourdhuiTogo,
  intervalleJours,
  joursInconnus,
  lectureJours,
  libelleJour,
  pageDeJours,
  totauxJours,
} from './jours';

const texte = (t: string) => t.replace(/\s+/g, ' ');

/** 28 jours du 18/12/2025 au 14/01/2026, inscriptions = rang du jour (1 à 28), NIU = 10 × rang. */
const DONNEES: InscriptionsParJour = (() => {
  const base = joursInconnus('2026-01-14');
  return {
    ...base,
    jours: base.jours.map((j, i) => ({ ...j, inscriptions: i + 1, niuGeneres: (i + 1) * 10 })),
  };
})();

describe('Inscriptions et NIU par jour', () => {
  it('donne 28 jours jusqu’à aujourd’hui, sans trou, même sans réponse de l’API', () => {
    const j = joursInconnus('2026-01-14').jours;
    expect(j).toHaveLength(28);
    expect(j[0].jour).toBe('2025-12-18');
    expect(j[27].jour).toBe('2026-01-14');
    expect(Number.isNaN(j[0].inscriptions)).toBe(true);
  });

  it('page 0 : aujourd’hui et les 6 jours précédents ; page 3 : trois semaines avant', () => {
    expect(pageDeJours(DONNEES, 0).map((j) => j.jour)).toEqual([
      '2026-01-08',
      '2026-01-09',
      '2026-01-10',
      '2026-01-11',
      '2026-01-12',
      '2026-01-13',
      '2026-01-14',
    ]);
    expect(pageDeJours(DONNEES, 3).map((j) => j.jour)[0]).toBe('2025-12-18');
    expect(pageDeJours(DONNEES, 3)).toHaveLength(7);
  });

  it('NIU inconnus tant que leur source n’est pas alimentée', () => {
    const p = pageDeJours({ ...DONNEES, niuDisponibles: false }, 0);
    expect(p.every((j) => Number.isNaN(j.niuGeneres))).toBe(true);
    expect(p[6].inscriptions).toBe(28);
  });

  it('libellés : jour de la semaine et date, intervalle en toutes lettres', () => {
    expect(libelleJour('2026-10-29')).toBe('jeu. 29/10');
    expect(libelleJour('2026-01-11')).toBe('dim. 11/01');
    expect(intervalleJours('2026-10-23', '2026-10-29')).toBe('Du 23 au 29 octobre');
    expect(intervalleJours('2026-09-30', '2026-10-06')).toBe('Du 30 septembre au 6 octobre');
    expect(intervalleJours('2026-01-01', '2026-01-07')).toBe('Du 1er au 7 janvier');
  });

  it('totaux et lecture de la page ; inconnus si aucun jour n’est connu', () => {
    // Page 0 : rangs 22 à 28.
    expect(totauxJours(pageDeJours(DONNEES, 0))).toEqual({ inscriptions: 175, niuGeneres: 1750 });
    expect(texte(lectureJours(pageDeJours(DONNEES, 0)))).toBe(
      texte('Du 8 au 14 janvier : 175 inscriptions, 1 750 NIU générés'),
    );
    expect(Number.isNaN(totauxJours(pageDeJours(joursInconnus('2026-01-14'), 0)).inscriptions)).toBe(true);
  });

  it('date du jour au Togo (UTC+0)', () => {
    expect(aujourdhuiTogo(new Date('2026-10-29T23:30:00Z'))).toBe('2026-10-29');
  });
});
