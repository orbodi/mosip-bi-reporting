import { describe, expect, it } from 'vitest';
import type { LigneMotif, MotifsArret } from '../api/client';
import {
  borneHauteDelaiH,
  colonnesArrets,
  etapeDuMotif,
  largeurBarre,
  SOURCE_AUTRES_CAS,
} from './traitement';

const ligne = (
  stage: string | null,
  motif: string | null,
  inscriptions: number,
  bloques = 0,
  autresEtapes = 0,
): LigneMotif => ({
  motif,
  libelle: motif ? `${motif} (fr)` : 'Autres cas',
  commentaire: motif ? `${motif} (MOSIP)` : null,
  piste: motif ? `${motif} (à vérifier)` : null,
  stage,
  stageLibelle: stage ? `${stage} (fr)` : null,
  autresEtapes,
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
    ligne('DemoDedupeStage', 'DOUBLON_ABIS', 55, 0, 2),
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
      [
        'DOUBLON_ABIS (fr)',
        'DemoDedupeStage (fr) et 2\u00a0autres étapes',
        'DOUBLON_ABIS (MOSIP)',
        'DOUBLON_ABIS (à vérifier)',
      ],
      ['Autres cas', SOURCE_AUTRES_CAS, null, null],
    ]);
    expect(rejets.lignes.map((l) => l.principale)).toEqual([true, false, false]);
    expect(rejets.lignes[1].part).toBeCloseTo(55 / 150);
    expect(rejets.lignes.map((l) => l.cle)).toEqual(['REFUS_SUPERVISEUR', 'DOUBLON_ABIS', 'autres']);
    expect(enCours.lignes[0]).toMatchObject({ principale: true, bloques: 590, valeur: 650 });
  });

  it('nomme l’étape principale, puis le nombre d’autres étapes où MOSIP pose le motif', () => {
    expect(etapeDuMotif('Vérification manuelle', 0)).toBe('Vérification manuelle');
    expect(etapeDuMotif('Vérification manuelle', 1)).toBe('Vérification manuelle et 1\u00a0autre étape');
    expect(etapeDuMotif('Vérification manuelle', 6)).toBe('Vérification manuelle et 6\u00a0autres étapes');
    expect(etapeDuMotif(null, 3)).toBeNull();
    expect(SOURCE_AUTRES_CAS).toBe('Motifs de moins de 1\u00a0% chacun');
  });

  it('colle « ; » et « : » au mot précédent dans les libellés et les pistes, pas dans le message de MOSIP', () => {
    const [rejets] = colonnesArrets({
      ...MOTIFS,
      rejets: [
        {
          ...ligne('OSIValidatorStage', 'IRIS', 10),
          libelle: 'Création du NIU refusée : donnée invalide',
          commentaire: 'Biometric data - Iris did not match',
          piste: 'Iris mal enregistré ; MOSIP ne dit pas laquelle.',
        },
      ],
    }).colonnes;
    expect(rejets.lignes[0]).toMatchObject({
      libelle: 'Création du NIU refusée\u00a0: donnée invalide',
      piste: 'Iris mal enregistré\u00a0; MOSIP ne dit pas laquelle.',
      commentaire: 'Biometric data - Iris did not match',
    });
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
