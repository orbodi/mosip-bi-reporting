import { describe, expect, it } from 'vitest';
import type { ArretsParEtape, PaquetsEnCours } from '../api/client';
import { borneHauteDelaiH, codeMosip, colonnesArrets, largeurBarre } from './traitement';

const ARRETS: ArretsParEtape = {
  perimetre: 'Ensemble du Togo',
  totalRejets: 150,
  totalEchecs: 50,
  rejets: [
    { code: 'REFUS_POSTE', libelle: 'Refus au poste', inscriptions: 90 },
    { code: 'DEMOGRAPHIC_VERIFICATION', libelle: 'Déduplication démographique', inscriptions: 55 },
    { code: null, libelle: 'Autres étapes', inscriptions: 5 },
  ],
  echecs: [{ code: 'OSI_VALIDATE', libelle: 'Validation opérateur et superviseur', inscriptions: 50 }],
};

const EN_COURS: PaquetsEnCours = {
  perimetre: 'Ensemble du Togo',
  seuilJours: 30,
  total: 800,
  bloques: 600,
  etapes: [
    { code: 'PACKET_RECEIVER', libelle: 'Réception du paquet', inscriptions: 100, bloques: 0 },
    { code: 'MANUAL_VERIFICATION', libelle: 'Vérification manuelle', inscriptions: 650, bloques: 590 },
    { code: null, libelle: 'Autres étapes', inscriptions: 50, bloques: 10 },
  ],
};

describe('Où s’arrêtent les paquets', () => {
  it('additionne les trois colonnes en paquets sans NIU, chacune avec sa part', () => {
    const { sansNiu, colonnes } = colonnesArrets(ARRETS, EN_COURS);
    expect(sansNiu).toBe(1000);
    expect(colonnes.map((c) => [c.titre, c.total, c.part])).toEqual([
      ['Rejetés', 150, 0.15],
      ['Échoués', 50, 0.05],
      ['En cours', 800, 0.8],
    ]);
    expect(colonnes[2].bloques).toBe(600);
  });

  it('garde l’ordre du traitement, met en avant la plus grosse étape, hors « Autres étapes »', () => {
    const [rejets, , enCours] = colonnesArrets(ARRETS, EN_COURS).colonnes;
    expect(rejets.lignes.map((l) => l.libelle)).toEqual([
      'Refus au poste',
      'Déduplication démographique',
      'Autres étapes',
    ]);
    expect(rejets.lignes.filter((l) => l.principale).map((l) => l.libelle)).toEqual(['Refus au poste']);
    expect(rejets.lignes[1].part).toBeCloseTo(55 / 150);
    expect(enCours.lignes[1]).toMatchObject({ principale: true, bloques: 590 });
    expect(
      colonnesArrets(ARRETS, { ...EN_COURS, etapes: [EN_COURS.etapes[2]] }).colonnes[2].lignes[0].principale,
    ).toBe(false);
  });

  it('montre les codes MOSIP, pas les codes propres au BI ni le regroupement', () => {
    expect(codeMosip('DEMOGRAPHIC_VERIFICATION')).toBe('DEMOGRAPHIC_VERIFICATION');
    expect(codeMosip('REFUS_POSTE')).toBeNull();
    expect(codeMosip(null)).toBeNull();
    const [rejets] = colonnesArrets(ARRETS, EN_COURS).colonnes;
    expect(rejets.lignes.map((l) => l.code)).toEqual([null, 'DEMOGRAPHIC_VERIFICATION', null]);
    expect(rejets.lignes.map((l) => l.cle)).toEqual(['REFUS_POSTE', 'DEMOGRAPHIC_VERIFICATION', 'autres']);
  });

  it('sans réponse de l’API : trois colonnes, totaux inconnus, aucune étape', () => {
    const { sansNiu, colonnes } = colonnesArrets(undefined, EN_COURS);
    expect(Number.isNaN(sansNiu)).toBe(true);
    expect(colonnes).toHaveLength(3);
    expect(Number.isNaN(colonnes[0].total)).toBe(true);
    expect(colonnes[0].lignes).toEqual([]);
    expect(Number.isNaN(colonnes[2].part)).toBe(true);
  });

  it('dessine des barres proportionnelles, vides pour une valeur inconnue ou un total nul', () => {
    expect(largeurBarre(55, 150)).toBeCloseTo(36.67, 1);
    expect(largeurBarre(5, 0)).toBe(0);
    expect(largeurBarre(Number.NaN, 10)).toBe(0);
    expect(largeurBarre(12, 10)).toBe(100);
  });
});

describe('Délais', () => {
  it('lit la borne haute de la classe : une heure sous 48 h, un jour au-delà', () => {
    expect(borneHauteDelaiH(8)).toBe(9);
    expect(borneHauteDelaiH(47)).toBe(48);
    expect(borneHauteDelaiH(240)).toBe(264);
    expect(Number.isNaN(borneHauteDelaiH(null))).toBe(true);
  });
});
