import { describe, expect, it } from 'vitest';
import { CLASSES_TAUX_NIU, alerteRejet, classeTauxNiu, cleNom, lectureZone, tauxNiu } from './territoire';

describe('classes de la carte', () => {
  it('range les taux de NIU dans les quatre classes de la maquette', () => {
    expect(classeTauxNiu(0.919)).toBe(0);
    expect(classeTauxNiu(0.92)).toBe(1);
    expect(classeTauxNiu(0.933)).toBe(2);
    expect(classeTauxNiu(0.943)).toBe(3);
    expect(CLASSES_TAUX_NIU.map((c) => c.libelle)).toEqual(['< 92 %', '92 à 93 %', '93 à 94 %', '94 % et +']);
  });

  it('laisse sans couleur une zone sans inscription', () => {
    expect(classeTauxNiu(tauxNiu({ inscriptions: 0, niuGeneres: 0, rejetees: 0 }))).toBe(-1);
  });
});

describe('alerte de rejet', () => {
  it('se déclenche à 3,5 % arrondi à une décimale', () => {
    // Savanes dans la maquette : 16 072 rejets sur 450 239 inscriptions = 3,57 % → ▲
    expect(alerteRejet({ inscriptions: 450239, niuGeneres: 0, rejetees: 16072 })).toBe(true);
    expect(alerteRejet({ inscriptions: 1000, niuGeneres: 0, rejetees: 35 })).toBe(true);
    expect(alerteRejet({ inscriptions: 10000, niuGeneres: 0, rejetees: 344 })).toBe(false);
    expect(alerteRejet({ inscriptions: 0, niuGeneres: 0, rejetees: 0 })).toBe(false);
  });
});

describe('cleNom', () => {
  it('compare les noms sans accents ni casse', () => {
    expect(cleNom('Tône')).toBe(cleNom('TONE'));
    expect(cleNom('Grand Lomé')).toBe('grandlome');
    expect(cleNom('Est-Mono')).toBe('estmono');
  });
});

describe('lectureZone', () => {
  it('donne le taux de NIU puis le nombre d’inscriptions', () => {
    expect(lectureZone('Kara', { inscriptions: 386000, niuGeneres: 358514, rejetees: 0 })).toBe(
      'Kara : 92,9\u00a0% de NIU générés, 386\u202f000 inscriptions',
    );
    expect(lectureZone('Oti', { inscriptions: 0, niuGeneres: 0, rejetees: 0 })).toBe(
      'Oti : aucune inscription sur la période',
    );
  });
});
