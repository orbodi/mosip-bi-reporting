import type { LigneMotif, MotifsArret } from '../api/client';
import { estConnu, INCONNUE } from './blocsVides';
import { nf, part, typographie } from './format';

export type CleArret = 'rejete' | 'echoue' | 'en-cours';

export interface LigneArret {
  /** Clé React : le motif, « autres » pour le regroupement « Autres cas ». */
  cle: string;
  /** Motif en français (« Rejeté par le superviseur du centre »). */
  libelle: string;
  /**
   * Étape principale en français, suivie du nombre d'autres étapes où MOSIP pose le motif (« Vérification manuelle
   * et 6 autres étapes ») ; pour « Autres cas », ce que la ligne regroupe.
   */
  etape: string | null;
  /** Message type de MOSIP pour ce motif (catalogue), null si aucun. */
  commentaire: string | null;
  /** Ce qu'il faut vérifier pour ce motif (catalogue), null pour « Autres cas ». */
  piste: string | null;
  valeur: number;
  /** Paquets en cours bloqués (colonne « En cours » seulement), sinon 0. */
  bloques: number;
  /** Part de la colonne. */
  part: number;
  /** Motif le plus fréquent de la colonne (première ligne, hors « Autres cas »). */
  principale: boolean;
  /** Ligne « Autres cas » (petits motifs regroupés par l'API). */
  autres: boolean;
}

export interface ColonneArret {
  cle: CleArret;
  titre: string;
  total: number;
  /** Part des paquets sans NIU. */
  part: number;
  /** Paquets bloqués (colonne « En cours »), sinon 0. */
  bloques: number;
  lignes: LigneArret[];
}

/** Seuil des petits motifs regroupés par l'API (EnrolementTraitementService.PART_MINIMALE_POURCENT). */
export const SOURCE_AUTRES_CAS = 'Motifs de moins de 1\u00a0% chacun';

/** « Vérification manuelle », « Vérification manuelle et 1 autre étape », « … et 6 autres étapes ». */
export function etapeDuMotif(stageLibelle: string | null | undefined, autresEtapes: number): string | null {
  if (!stageLibelle) return null;
  if (autresEtapes <= 0) return stageLibelle;
  const autres = autresEtapes === 1 ? 'autre étape' : 'autres étapes';
  return `${stageLibelle} et ${nf(autresEtapes)}\u00a0${autres}`;
}

/**
 * Colonnes du bloc « Où s'arrêtent les paquets » (GET /enrolement/motifs) : rejetés, échoués, en cours, chacune avec
 * une ligne par motif (toutes étapes confondues) dans l'ordre de l'API (du plus fréquent au moins fréquent, « Autres
 * cas » en dernier). Libellés et pistes avec la ponctuation française. Les paquets sans NIU sont la somme des trois
 * totaux. Sans réponse de l'API, la colonne garde son titre, total inconnu (affiché 0) et aucune ligne.
 */
export function colonnesArrets(motifs?: MotifsArret): { sansNiu: number; colonnes: ColonneArret[] } {
  const brutes: { cle: CleArret; titre: string; total: number; bloques: number; lignes: LigneMotif[] }[] = [
    {
      cle: 'rejete',
      titre: 'Rejetés',
      total: motifs ? motifs.totalRejets : INCONNUE,
      bloques: 0,
      lignes: motifs?.rejets ?? [],
    },
    {
      cle: 'echoue',
      titre: 'Échoués',
      total: motifs ? motifs.totalEchecs : INCONNUE,
      bloques: 0,
      lignes: motifs?.echecs ?? [],
    },
    {
      cle: 'en-cours',
      titre: 'En cours',
      total: motifs ? motifs.totalEnCours : INCONNUE,
      bloques: motifs ? motifs.bloques : INCONNUE,
      lignes: motifs?.enCours ?? [],
    },
  ];
  const sansNiu = motifs ? brutes.reduce((s, c) => s + c.total, 0) : INCONNUE;
  return {
    sansNiu,
    colonnes: brutes.map((c) => ({
      cle: c.cle,
      titre: c.titre,
      total: c.total,
      part: part(c.total, sansNiu),
      bloques: c.bloques,
      lignes: c.lignes.map((l, i) => ({
        cle: l.motif ?? 'autres',
        libelle: typographie(l.libelle),
        etape: l.motif ? etapeDuMotif(l.stageLibelle, l.autresEtapes) : SOURCE_AUTRES_CAS,
        commentaire: l.commentaire ?? null,
        piste: l.piste ? typographie(l.piste) : null,
        valeur: l.inscriptions,
        bloques: l.bloques,
        part: part(l.inscriptions, c.total),
        principale: i === 0 && !!l.motif && l.inscriptions > 0,
        autres: !l.motif,
      })),
    })),
  };
}

/** Largeur d'une barre en % de la piste : 0 si la valeur ou le total sont inconnus ou nuls. */
export function largeurBarre(valeur: number, total: number): number {
  return estConnu(valeur) && estConnu(total) && total > 0 ? Math.min(100, (valeur / total) * 100) : 0;
}

/**
 * Borne haute (exclue) de la classe de délai dont l'API donne la borne basse : classes d'une heure sous 48 h, d'un
 * jour au-delà (bi.fait_delai_jour). « 9 sur 10 en moins de N h » se lit sur cette borne : la borne basse seule
 * dirait moins de 9 sur 10. Inconnue si la borne basse l'est.
 */
export function borneHauteDelaiH(borneBasse?: number | null): number {
  if (borneBasse == null) return INCONNUE;
  return borneBasse < 48 ? borneBasse + 1 : borneBasse + 24;
}
