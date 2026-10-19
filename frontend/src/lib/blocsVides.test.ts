import { describe, expect, it } from 'vitest';
import { nf, part, pct } from './format';
import { devenirInconnu, lundisDesSemainesCompletes, semainesInconnues } from './blocsVides';

describe('données de remplacement', () => {
  it('calcule les 12 semaines complètes comme l’API', () => {
    const lundis = lundisDesSemainesCompletes('2026-01-14');
    expect(lundis).toHaveLength(12);
    expect(lundis[0]).toBe('2025-10-20');
    expect(lundis[11]).toBe('2026-01-05');
    expect(lundisDesSemainesCompletes('2026-01-11')[11]).toBe('2026-01-05');
    expect(lundisDesSemainesCompletes('2026-01-12')[11]).toBe('2026-01-05');
  });

  it('affiche des tirets, jamais des zéros', () => {
    const d = devenirInconnu();
    expect(nf(d.inscriptions)).toBe('–');
    expect(pct(part(d.niuGeneres, d.inscriptions))).toBe('–');
    expect(semainesInconnues('2026-01-14').semaines.every((s) => Number.isNaN(s.inscriptions))).toBe(true);
  });
});
