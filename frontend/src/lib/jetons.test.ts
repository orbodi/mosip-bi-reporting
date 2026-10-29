import { describe, expect, it } from 'vitest';
import { eclaircir } from './jetons';

describe('eclaircir', () => {
  it('mêle la couleur de blanc, sans toucher à ce qui n’est pas « #rrggbb »', () => {
    expect(eclaircir('#000000', 0.5)).toBe('#808080');
    expect(eclaircir('#1f4e8c', 0)).toBe('#1f4e8c');
    expect(eclaircir('#1F4E8C', 1)).toBe('#ffffff');
    expect(eclaircir('', 0.6)).toBe('');
    expect(eclaircir('var(--bleu)', 0.6)).toBe('var(--bleu)');
  });
});
