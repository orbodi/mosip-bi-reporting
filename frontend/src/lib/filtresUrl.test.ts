import { describe, expect, it } from 'vitest';
import { validerFiltres } from './filtresUrl';

describe('filtres de l’adresse', () => {
  it('écarte la période d’un ancien lien et garde la région ouverte', () => {
    expect(validerFiltres({ periode: '7j', du: '2026-01-01', au: '2026-01-31', region: 'KAR' })).toEqual({
      region: 'KAR',
    });
  });

  it('écarte un code de région mal formé', () => {
    expect(validerFiltres({ region: 'KAR;drop' })).toEqual({ region: undefined });
  });

  it('garde la zone ouverte dans le bloc Territoire, à tout niveau', () => {
    expect(validerFiltres({ zone: '10011' })).toEqual({ zone: '10011' });
    expect(validerFiltres({ zone: 'T-CAN 1' })).toEqual({});
  });
});
