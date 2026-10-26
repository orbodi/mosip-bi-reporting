import type { ArretsParEtape, PaquetsEnCours } from '../api/client';
import { estConnu, INCONNUE } from './blocsVides';
import { part } from './format';

/** Codes d'étape propres au BI, qui ne sont pas des codes MOSIP : jamais montrés en complément du libellé. */
const CODES_HORS_MOSIP = new Set(['REFUS_POSTE']);

/** Code MOSIP à montrer à côté du libellé d'une étape, ou null (« Autres étapes », codes propres au BI). */
export const codeMosip = (code?: string | null): string | null =>
  code && !CODES_HORS_MOSIP.has(code) ? code : null;

export type CleArret = 'rejete' | 'echoue' | 'en-cours';

export interface LigneArret {
  /** Clé React : code de l'étape, « autres » pour le regroupement. */
  cle: string;
  libelle: string;
  code: string | null;
  valeur: number;
  /** Paquets en cours bloqués à cette étape (colonne « En cours » seulement), sinon 0. */
  bloques: number;
  /** Part de la colonne. */
  part: number;
  /** Étape qui retient le plus de paquets de la colonne (hors « Autres étapes »), mise en gras. */
  principale: boolean;
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

/**
 * Colonnes du bloc « Où s'arrêtent les paquets » : rejetés et échoués (GET /enrolement/etapes), en cours
 * (GET /enrolement/en-cours), chacune dans l'ordre du traitement que donne l'API. Les paquets sans NIU sont la somme
 * des trois totaux. Sans réponse de l'API, la colonne garde son titre, total inconnu (affiché 0) et aucune étape.
 */
export function colonnesArrets(
  arrets?: ArretsParEtape,
  enCours?: PaquetsEnCours,
): { sansNiu: number; colonnes: ColonneArret[] } {
  const brutes: { cle: CleArret; titre: string; total: number; bloques: number; lignes: LigneBrute[] }[] = [
    {
      cle: 'rejete',
      titre: 'Rejetés',
      total: arrets ? arrets.totalRejets : INCONNUE,
      bloques: 0,
      lignes: (arrets?.rejets ?? []).map((e) => ({ ...e, bloques: 0 })),
    },
    {
      cle: 'echoue',
      titre: 'Échoués',
      total: arrets ? arrets.totalEchecs : INCONNUE,
      bloques: 0,
      lignes: (arrets?.echecs ?? []).map((e) => ({ ...e, bloques: 0 })),
    },
    {
      cle: 'en-cours',
      titre: 'En cours',
      total: enCours ? enCours.total : INCONNUE,
      bloques: enCours ? enCours.bloques : INCONNUE,
      lignes: enCours?.etapes ?? [],
    },
  ];
  const sansNiu = brutes.every((c) => estConnu(c.total)) ? brutes.reduce((s, c) => s + c.total, 0) : INCONNUE;
  return {
    sansNiu,
    colonnes: brutes.map((c) => ({
      cle: c.cle,
      titre: c.titre,
      total: c.total,
      part: part(c.total, sansNiu),
      bloques: c.bloques,
      lignes: lignesColonne(c.lignes, c.total),
    })),
  };
}

interface LigneBrute {
  code?: string | null;
  libelle: string;
  inscriptions: number;
  bloques: number;
}

function lignesColonne(lignes: LigneBrute[], total: number): LigneArret[] {
  const principale = lignes.reduce<LigneBrute | undefined>(
    (max, l) => (l.code && l.inscriptions > 0 && (!max || l.inscriptions > max.inscriptions) ? l : max),
    undefined,
  );
  return lignes.map((l) => ({
    cle: l.code ?? 'autres',
    libelle: l.libelle,
    code: codeMosip(l.code),
    valeur: l.inscriptions,
    bloques: l.bloques,
    part: part(l.inscriptions, total),
    principale: l === principale,
  }));
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
