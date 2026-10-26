import { describe, expect, it } from 'vitest';
import { numerosDePage, paginer } from './pagination';

const lignes = Array.from({ length: 137 }, (_, i) => i + 1);

describe('pagination', () => {
  it('découpe en pages de 10 ou 20 et décrit les lignes affichées', () => {
    expect(paginer(lignes, 0, 20)).toMatchObject({ page: 0, pages: 7, debut: 1, fin: 20, total: 137 });
    expect(paginer(lignes, 6, 20)).toMatchObject({ debut: 121, fin: 137, lignes: lignes.slice(120) });
    expect(paginer(lignes, 2, 10).lignes).toEqual([21, 22, 23, 24, 25, 26, 27, 28, 29, 30]);
  });

  it('ramène une page hors limites à la dernière, et gère un tableau vide', () => {
    expect(paginer(lignes, 99, 20).page).toBe(6);
    expect(paginer(lignes, -3, 20).page).toBe(0);
    expect(paginer([], 0, 20)).toMatchObject({ page: 0, pages: 1, debut: 0, fin: 0, total: 0 });
  });

  it('montre la première, la dernière et les voisines de la page courante', () => {
    expect(numerosDePage(0, 1)).toEqual([0]);
    expect(numerosDePage(0, 4)).toEqual([0, 1, 2, 3]);
    expect(numerosDePage(5, 14)).toEqual([0, '…', 4, 5, 6, '…', 13]);
    // Un trou d'une seule page affiche la page plutôt que « … ».
    expect(numerosDePage(3, 14)).toEqual([0, 1, 2, 3, 4, '…', 13]);
  });
});
