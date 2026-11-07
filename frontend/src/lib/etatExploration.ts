import {
  DIMENSIONS,
  SEXES,
  SOURCES,
  TRANCHES_AGE,
  type CleDimension,
  type SourceExploration,
} from '../pages/exploration/catalogue';

/**
 * Choix de l'Exploration portés par l'adresse (décision du 05/11/2026, lot A) : un lien rouvre la même vue, Retour et
 * rechargement la gardent. Clés lisibles, absentes quand elles valent leur défaut :
 * ?source=cartes&indicateurs=dem,exp&quand=R:moisprec&zones=SAV.SAV-02&par=mois&valeurs=pt&tri=dem:desc&sexe=F
 */
export type Mode = 'n' | 'pt' | 'pf';
export type Perimetre = 'usagers' | 'paquets';

export interface EtatExploration {
  source: SourceExploration['cle'];
  /** Clés des indicateurs choisis, dans l'ordre du catalogue ; jamais vide. */
  indicateurs: string[];
  /** Valeur du filtre Période (lib/periodeExploration) : tout, A:…, M:…, P:…, R:…. */
  periode: string;
  filtres: Partial<Record<CleDimension, string>>;
  /** Authentifications : usagers ou traitement des paquets, jamais additionnés. */
  perimetre: Perimetre;
  /** Zones choisies, de la région vers le centre (codes bi.zone). */
  chemin: string[];
  /** Ventilation demandée ; undefined : la première proposée. */
  par?: string;
  mode: Mode;
  /** Tri du tableau : « libelle » ou clé d'indicateur, puis le sens ; undefined : ordre naturel. */
  tri?: { colonne: string; sens: 'asc' | 'desc' };
}

/** Paramètres de l'adresse propres à l'Exploration (chaînes validées par validerExploration). */
export interface RechercheExploration {
  source?: string;
  indicateurs?: string;
  quand?: string;
  perimetre?: string;
  zones?: string;
  par?: string;
  valeurs?: string;
  tri?: string;
  sexe?: string;
  age?: string;
  nat?: string;
  type?: string;
  taut?: string;
  cause?: string;
  part?: string;
  terr?: string;
}

export const CLES_EXPLORATION: (keyof RechercheExploration)[] = [
  'source',
  'indicateurs',
  'quand',
  'perimetre',
  'zones',
  'par',
  'valeurs',
  'tri',
  ...(Object.keys(DIMENSIONS) as CleDimension[]),
];

const CODE_ZONE = /^[A-Za-z0-9_-]{1,40}$/;
const PERIODE = /^(tout|A:\d{4}|M:\d{4}-\d{2}|P:(\d{4}-\d{2}-\d{2})?:(\d{4}-\d{2}-\d{2})?|R:(30j|mois|moisprec|annee))$/;
const CLE = /^[a-z]{1,12}$/;

/** Le routeur lit « 2026 » ou « 10011 » comme des nombres : on les remet en texte. */
const texte = (v: unknown): string | undefined =>
  typeof v === 'string' ? v : typeof v === 'number' && Number.isFinite(v) ? String(v) : undefined;

/**
 * Paramètres de l'Exploration retenus dans l'adresse : formes attendues seulement (une valeur de filtre est un
 * libellé ou un code court, sans caractère de contrôle). Les valeurs sont ensuite confrontées au catalogue par
 * lireEtat.
 */
export function validerExploration(recherche: Record<string, unknown>): RechercheExploration {
  const garder = (cle: string, motif: RegExp) => {
    const v = texte(recherche[cle]);
    return v !== undefined && motif.test(v) ? v : undefined;
  };
  const resultat: RechercheExploration = {
    source: garder('source', CLE),
    indicateurs: garder('indicateurs', /^[a-z]{1,8}(,[a-z]{1,8}){0,11}$/),
    quand: garder('quand', PERIODE),
    perimetre: garder('perimetre', /^(usagers|paquets)$/),
    zones: garder('zones', /^[A-Za-z0-9_-]{1,40}(\.[A-Za-z0-9_-]{1,40}){0,5}$/),
    par: garder('par', CLE),
    valeurs: garder('valeurs', /^(n|pt|pf)$/),
    tri: garder('tri', /^[a-z]{1,8}:(asc|desc)$/),
  };
  for (const d of Object.keys(DIMENSIONS) as CleDimension[]) {
    // eslint-disable-next-line no-control-regex
    resultat[d] = garder(d, /^[^\u0000-\u001f]{1,120}$/);
  }
  return Object.fromEntries(Object.entries(resultat).filter(([, v]) => v !== undefined));
}

/** Ventilation par défaut d'une source : sous-zone si son premier indicateur se ventile par territoire, sinon mois. */
const parDefaut = (s: SourceExploration) => (s.indicateurs[0].territoire ? 'sous' : 'mois');

/** Sexe et tranche d'âge : codes de l'API seulement (un ancien lien « sexe=Femmes » est écarté). */
const valeurConnue = (d: CleDimension, v: string) =>
  d === 'sexe' ? SEXES.some((s) => s.id === v) : d === 'age' ? TRANCHES_AGE.some((t) => t.id === v) : true;

/** État de l'Exploration lu dans l'adresse, confronté au catalogue (valeurs inconnues écartées, défauts sinon). */
export function lireEtat(r: RechercheExploration): EtatExploration {
  const source = SOURCES.find((s) => s.cle === r.source) ?? SOURCES[0];
  const demandes = (r.indicateurs ?? '').split(',');
  const indicateurs = source.indicateurs.map((i) => i.cle).filter((c) => demandes.includes(c));
  // Filtres de la source, sauf ceux sans données dans l'Exploration (un ancien lien ne doit pas tout mettre à 0).
  const sansDonnees = source.indisponibles?.dimensions ?? [];
  const dimensions = new Set(source.indicateurs.flatMap((i) => i.dimensions).filter((d) => !sansDonnees.includes(d)));
  const filtres: EtatExploration['filtres'] = {};
  for (const d of dimensions) if (r[d] && valeurConnue(d, r[d])) filtres[d] = r[d];
  const [colonne, sens] = (r.tri ?? '').split(':');
  const colonneConnue = colonne === 'libelle' || source.indicateurs.some((i) => i.cle === colonne);
  return {
    source: source.cle,
    indicateurs: indicateurs.length ? indicateurs : [source.indicateurs[0].cle],
    periode: r.quand ?? 'tout',
    filtres,
    perimetre: r.perimetre === 'paquets' ? 'paquets' : 'usagers',
    chemin:
      r.zones && source.indicateurs.some((i) => i.territoire)
        ? r.zones.split('.').filter((z) => CODE_ZONE.test(z))
        : [],
    par: r.par && r.par !== parDefaut(source) ? r.par : undefined,
    mode: r.valeurs === 'pt' || r.valeurs === 'pf' ? r.valeurs : 'n',
    tri: colonneConnue && (sens === 'asc' || sens === 'desc') ? { colonne, sens } : undefined,
  };
}

/** Paramètres de l'adresse d'un état, sans ceux qui valent leur défaut (toutes les clés présentes, undefined sinon). */
export function ecrireRecherche(e: EtatExploration): Record<keyof RechercheExploration, string | undefined> {
  const source = SOURCES.find((s) => s.cle === e.source) ?? SOURCES[0];
  const indicateurs = e.indicateurs.join(',');
  const dims = Object.fromEntries(
    (Object.keys(DIMENSIONS) as CleDimension[]).map((d) => [d, e.filtres[d] || undefined]),
  ) as Record<CleDimension, string | undefined>;
  return {
    source: e.source === SOURCES[0].cle ? undefined : e.source,
    indicateurs: indicateurs === source.indicateurs[0].cle ? undefined : indicateurs,
    quand: e.periode === 'tout' ? undefined : e.periode,
    perimetre: e.source === 'auth' && e.perimetre === 'paquets' ? 'paquets' : undefined,
    zones: e.chemin.length ? e.chemin.join('.') : undefined,
    par: e.par && e.par !== parDefaut(source) ? e.par : undefined,
    valeurs: e.mode === 'n' ? undefined : e.mode,
    tri: e.tri ? `${e.tri.colonne}:${e.tri.sens}` : undefined,
    ...dims,
  };
}

/** Changement de source : indicateurs, filtres, zones, ventilation et tri repartent de zéro ; la période reste. */
export function changerSource(e: EtatExploration, cle: string): EtatExploration {
  const source = SOURCES.find((s) => s.cle === cle) ?? SOURCES[0];
  return {
    source: source.cle,
    indicateurs: [source.indicateurs[0].cle],
    periode: e.periode,
    filtres: {},
    perimetre: 'usagers',
    chemin: [],
    par: undefined,
    mode: 'n',
    tri: undefined,
  };
}

/** Coche ou décoche un indicateur ; le dernier reste coché ; ordre du catalogue. */
export function basculerIndicateur(e: EtatExploration, cle: string): EtatExploration {
  const source = SOURCES.find((s) => s.cle === e.source) ?? SOURCES[0];
  if (e.indicateurs.includes(cle)) {
    return e.indicateurs.length > 1 ? { ...e, indicateurs: e.indicateurs.filter((x) => x !== cle) } : e;
  }
  const indicateurs = source.indicateurs.map((i) => i.cle).filter((x) => x === cle || e.indicateurs.includes(x));
  return { ...e, indicateurs };
}

/** Réinitialiser : la source sans filtre, toute la période, premier indicateur. */
export const reinitialiser = (e: EtatExploration): EtatExploration => ({
  ...changerSource(e, e.source),
  periode: 'tout',
});

/** Tri suivant au clic sur un titre de colonne : décroissant, croissant, puis ordre naturel. */
export function trierPar(e: EtatExploration, colonne: string): EtatExploration {
  if (e.tri?.colonne !== colonne) return { ...e, tri: { colonne, sens: colonne === 'libelle' ? 'asc' : 'desc' } };
  const premier = colonne === 'libelle' ? 'asc' : 'desc';
  return { ...e, tri: e.tri.sens === premier ? { colonne, sens: premier === 'asc' ? 'desc' : 'asc' } : undefined };
}

const ordreFr = new Intl.Collator('fr', { sensitivity: 'base', numeric: true });

/**
 * Lignes du tableau dans l'ordre demandé : par libellé (ordre alphabétique français) ou par la valeur d'un
 * indicateur (valeur inconnue en dernier) ; sans tri, l'ordre reçu (référentiel, temps ou API).
 */
export function trierLignes<L extends { libelle: string; valeurs: number[] }>(
  lignes: L[],
  tri: EtatExploration['tri'],
  colonnes: string[],
): L[] {
  if (!tri) return lignes;
  const j = colonnes.indexOf(tri.colonne);
  const signe = tri.sens === 'asc' ? 1 : -1;
  return lignes
    .map((l, i) => ({ l, i }))
    .sort((a, b) => {
      if (tri.colonne === 'libelle') return signe * ordreFr.compare(a.l.libelle, b.l.libelle) || a.i - b.i;
      if (j < 0) return a.i - b.i;
      const [va, vb] = [a.l.valeurs[j], b.l.valeurs[j]];
      const [ka, kb] = [Number.isFinite(va), Number.isFinite(vb)];
      if (ka !== kb) return ka ? -1 : 1;
      return (ka ? signe * (va - vb) : 0) || a.i - b.i;
    })
    .map(({ l }) => l);
}
