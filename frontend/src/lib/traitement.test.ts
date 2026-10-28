import { describe, expect, it } from 'vitest';
import type { LigneMotif, MotifsArret } from '../api/client';
import { borneHauteDelaiH, colonnesArrets, largeurBarre } from './traitement';

const ligne = (
  stage: string | null,
  motif: string | null,
  inscriptions: number,
  bloques = 0,
): LigneMotif => ({
  motif,
  libelle: motif ? `${motif} (fr)` : 'Autres cas',
  commentaire: motif ? `${motif} (MOSIP)` : null,
  piste: motif ? `${motif} (à vérifier)` : null,
  stage,
  stageLibelle: stage ? `${stage} (fr)` : null,
  inscriptions,
  bloques,
});

const MOTIFS: MotifsArret = {
  perimetre: 'Ensemble du Togo',
  seuilJours: 30,
  totalRejets: 150,
  totalEchecs: 50,
  totalEnCours: 800,
  bloques: 600,
  rejets: [
    ligne('PacketValidatorStage', 'REFUS_SUPERVISEUR', 90),
    ligne('DemoDedupeStage', 'DOUBLON_ABIS', 55),
    ligne(null, null, 5),
  ],
  echecs: [ligne('OSIValidatorStage', 'BIOMETRIE_NON_CONCORDANTE', 50)],
  enCours: [
    ligne('BioDedupeStage', 'FILE_VERIF_MANUELLE', 650, 590),
    ligne('PacketReceiverStage', 'RECU_EN_ATTENTE', 100),
    ligne(null, null, 50, 10),
  ],
};

describe('Où s’arrêtent les paquets', () => {
  it('additionne les trois colonnes en paquets sans NIU, chacune avec sa part', () => {
    const { sansNiu, colonnes } = colonnesArrets(MOTIFS);
    expect(sansNiu).toBe(1000);
    expect(colonnes.map((c) => [c.titre, c.total, c.part])).toEqual([
      ['Rejetés', 150, 0.15],
      ['Échoués', 50, 0.05],
      ['En cours', 800, 0.8],
    ]);
    expect(colonnes[2].bloques).toBe(600);
  });

  it('garde l’ordre de l’API (du plus fréquent au moins fréquent) et met en avant le premier motif', () => {
    const [rejets, , enCours] = colonnesArrets(MOTIFS).colonnes;
    expect(rejets.lignes.map((l) => [l.libelle, l.etape, l.commentaire, l.piste])).toEqual([
      [
        'REFUS_SUPERVISEUR (fr)',
        'PacketValidatorStage (fr)',
        'REFUS_SUPERVISEUR (MOSIP)',
        'REFUS_SUPERVISEUR (à vérifier)',
      ],
      ['DOUBLON_ABIS (fr)', 'DemoDedupeStage (fr)', 'DOUBLON_ABIS (MOSIP)', 'DOUBLON_ABIS (à vérifier)'],
      ['Autres cas', null, null, null],
    ]);
    expect(rejets.lignes.map((l) => l.principale)).toEqual([true, false, false]);
    expect(rejets.lignes[1].part).toBeCloseTo(55 / 150);
    expect(rejets.lignes.map((l) => l.cle)).toEqual([
      'PacketValidatorStage:REFUS_SUPERVISEUR',
      'DemoDedupeStage:DOUBLON_ABIS',
      'autres',
    ]);
    expect(enCours.lignes[0]).toMatchObject({ principale: true, bloques: 590, valeur: 650 });
  });

  it('« Autres cas » seul en tête n’est pas mis en avant', () => {
    const { colonnes } = colonnesArrets({ ...MOTIFS, echecs: [ligne(null, null, 50)] });
    expect(colonnes[1].lignes[0].principale).toBe(false);
  });

  it('sans réponse de l’API : trois colonnes, totaux inconnus, aucune ligne', () => {
    const { sansNiu, colonnes } = colonnesArrets(undefined);
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
