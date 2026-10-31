import type { DevenirInscriptions, InscriptionsParSemaine, LigneZone, Territoire } from '../api/client';

/**
 * Données de remplacement quand l'API ne répond pas (ou pas encore) : les blocs gardent leur mise en page (cartes,
 * axes, carte, tableau) avec des valeurs inconnues. NaN s'affiche 0 (lib/format.ts, décision du 20/10/2026) mais ne
 * colore rien et ne dessine aucune barre : la forme des graphiques n'est jamais estimée.
 */
const INCONNU = Number.NaN;

const chiffresInconnus = {
  inscriptions: INCONNU,
  niuGeneres: INCONNU,
  enCours: INCONNU,
  echouees: INCONNU,
  rejetees: INCONNU,
  nonClassees: INCONNU,
};

/** Vrai si un nombre de l'API est connu (faux pour les données de remplacement). */
export const estConnu = (n: number) => Number.isFinite(n);

export function devenirInconnu(perimetre = 'Ensemble du Togo'): DevenirInscriptions {
  return {
    perimetre,
    ...chiffresInconnus,
    enReprocessing: INCONNU,
    demandesMiseAJour: INCONNU,
    demandesNiuPerdu: INCONNU,
  };
}

const versIso = (d: Date) => d.toISOString().slice(0, 10);

/**
 * Lundis des 12 semaines complètes qui finissent au plus tard le jour {@code fin} (« aaaa-mm-jj »), comme l'API
 * (EnrolementService.lundisDesSemainesCompletes).
 */
export function lundisDesSemainesCompletes(fin: string, nombre = 12): string[] {
  const jour = new Date(`${fin}T00:00:00Z`);
  const jourSemaine = (jour.getUTCDay() + 6) % 7; // 0 = lundi … 6 = dimanche
  const dernierLundi = new Date(jour);
  dernierLundi.setUTCDate(jour.getUTCDate() - (jourSemaine === 6 ? 6 : jourSemaine + 7));
  return Array.from({ length: nombre }, (_, k) => {
    const lundi = new Date(dernierLundi);
    lundi.setUTCDate(dernierLundi.getUTCDate() - 7 * (nombre - 1 - k));
    return versIso(lundi);
  });
}

export function semainesInconnues(fin: string, perimetre = 'Ensemble du Togo'): InscriptionsParSemaine {
  return {
    perimetre,
    niuDisponibles: true,
    semaines: lundisDesSemainesCompletes(fin).map((lundi) => ({
      lundi,
      dansLaPeriode: true,
      inscriptions: INCONNU,
      niuGeneres: INCONNU,
    })),
  };
}

/** Zones connues sans leurs chiffres (codes du filtre Région quand ils sont chargés, sinon les noms des contours). */
export function territoireInconnu(
  perimetre: string,
  zones: { code: string; nom: string }[],
  niveau: string,
): Territoire {
  const lignes: LigneZone[] = zones.map((z) => ({
    code: z.code,
    nom: z.nom,
    niveau,
    horsReferentiel: false,
    ...chiffresInconnus,
    preinscriptions: INCONNU,
    ouvrable: niveau !== 'centre',
  }));
  return { perimetre, ascendants: [], ...chiffresInconnus, preinscriptions: INCONNU, lignes };
}

/** Semaine d'un graphique hebdomadaire générique (composants/blocs/GraphiqueHebdo). */
export interface SemaineValeurs {
  lundi: string;
  valeurs: Record<string, number>;
}

/** Les 12 semaines complètes jusqu'à {@code fin}, chaque série inconnue (affichée 0). */
export function semainesVides(fin: string, cles: string[]): SemaineValeurs[] {
  return lundisDesSemainesCompletes(fin).map((lundi) => ({
    lundi,
    valeurs: Object.fromEntries(cles.map((c) => [c, INCONNU])),
  }));
}

/** Valeur inconnue (API absente ou source non raccordée) : affichée 0 (décision du 20/10/2026). */
export const INCONNUE = INCONNU;

/** Tranches d'âge de la pyramide, de la plus âgée à la plus jeune (libellés de la maquette Enrôlement). */
export const TRANCHES_PYRAMIDE = [
  '60 ans et +',
  '46 à 60',
  '36 à 45',
  '26 à 35',
  '19 à 25',
  '15 à 18',
  '6 à 14',
  '0 à 5',
] as const;

/** Une ligne de la pyramide des âges (composants/blocs/Pyramide). */
export interface TrancheSexe {
  tranche: string;
  femmes: number;
  hommes: number;
}

/** Les tranches de la pyramide sans leurs chiffres (sexe et âge sans source : CLAUDE.md, règle « Sexe et âge »). */
export function pyramideInconnue(): TrancheSexe[] {
  return TRANCHES_PYRAMIDE.map((tranche) => ({ tranche, femmes: INCONNU, hommes: INCONNU }));
}

/**
 * Longueur d'une barre de la pyramide, en % de sa demi-largeur : la plus grande valeur des deux sexes occupe 70 %
 * (comme la maquette), le reste laisse la place au nombre. 0 pour une valeur inconnue.
 */
export function largeurPyramide(valeur: number, lignes: TrancheSexe[]): number {
  const connues = lignes.flatMap((l) => [l.femmes, l.hommes]).filter(estConnu);
  const max = Math.max(0, ...connues);
  return estConnu(valeur) && max > 0 ? (valeur / max) * 70 : 0;
}

/** Nombre de l'API : null ou absent (« non disponible ») devient la valeur inconnue, affichée 0 ; 0 reste 0. */
export const depuisApi = (n?: number | null): number => n ?? INCONNU;

/** Codes de tranche de l'API (GET /api/v1/enrolement/age-sexe) → libellés de la pyramide. */
const LIBELLE_TRANCHE: Record<string, (typeof TRANCHES_PYRAMIDE)[number]> = {
  '60+': '60 ans et +',
  '46-60': '46 à 60',
  '36-45': '36 à 45',
  '26-35': '26 à 35',
  '19-25': '19 à 25',
  '15-18': '15 à 18',
  '6-14': '6 à 14',
  '0-5': '0 à 5',
};

/**
 * Lignes de la pyramide depuis l'API, de la plus âgée à la plus jeune. Sans réponse, ou source non disponible :
 * les huit tranches sans chiffres. Une tranche absente de la réponse reste inconnue, jamais 0.
 */
export function lignesPyramide(api?: {
  disponible: boolean;
  tranches: { tranche: string; femmes?: number | null; hommes?: number | null }[];
}): TrancheSexe[] {
  if (!api?.disponible) return pyramideInconnue();
  const parLibelle = new Map(api.tranches.map((t) => [LIBELLE_TRANCHE[t.tranche], t]));
  return TRANCHES_PYRAMIDE.map((tranche) => {
    const t = parLibelle.get(tranche);
    return { tranche, femmes: depuisApi(t?.femmes), hommes: depuisApi(t?.hommes) };
  });
}

/** Dernière ligne de la pyramide des pré-inscrits : sexe connu, âge non renseigné (tranche « inconnu » de l'API). */
export const LIGNE_AGE_INCONNU = 'Âge inconnu';

/**
 * Pyramide suivie d'une ligne « Âge inconnu » : ses totaux femmes et hommes égalent alors tous les dossiers dont
 * le sexe est connu. Sans réponse ou source non disponible, cette ligne reste inconnue comme les autres.
 */
export function lignesPyramideAvecAgeInconnu(api?: Parameters<typeof lignesPyramide>[0]): TrancheSexe[] {
  const inconnu = api?.disponible ? api.tranches.find((t) => t.tranche === 'inconnu') : undefined;
  return [
    ...lignesPyramide(api),
    { tranche: LIGNE_AGE_INCONNU, femmes: depuisApi(inconnu?.femmes), hommes: depuisApi(inconnu?.hommes) },
  ];
}
