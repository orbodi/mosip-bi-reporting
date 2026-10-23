import { describe, expect, it } from 'vitest';
import { dernierRafraichissement } from './fraicheur';

describe('dernier rafraîchissement d’une page', () => {
  const sources = [
    { source: 'enrolement', dernierChargement: null },
    { source: 'preinscription', dernierChargement: '2026-10-23T15:05:12Z' },
    { source: 'cartes', dernierChargement: '2026-10-23T16:00:00+01:00' },
    { source: 'abis', dernierChargement: '2026-10-23T14:00:00Z' },
  ];

  it('prend le chargement le plus récent des sources de la page, fuseaux compris', () => {
    expect(dernierRafraichissement(sources, ['enrolement', 'preinscription'])).toBe('2026-10-23T15:05:12Z');
    expect(dernierRafraichissement(sources, ['preinscription', 'cartes', 'abis'])).toBe('2026-10-23T15:05:12Z');
  });

  it('reste indéfini tant qu’aucune source de la page n’est chargée', () => {
    expect(dernierRafraichissement(sources, ['enrolement'])).toBeUndefined();
    expect(dernierRafraichissement([], ['idps'])).toBeUndefined();
  });
});
