/**
 * Formats d'affichage du BI (règles de CLAUDE.md) : nombres fr-FR avec espace fine insécable,
 * pourcentages à une décimale, dates jj/mm/aaaa, heures « 11h59 », heure du Togo (UTC+0).
 */
const ESPACE_FINE = '\u202f';
const ESPACE_INSECABLE = '\u00a0';
const FUSEAU = 'Africa/Lome';

const formatNombre = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 });
const formatDate = new Intl.DateTimeFormat('fr-FR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  timeZone: FUSEAU,
});
const formatJourMois = new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'long', timeZone: FUSEAU });
const formatJourMoisCourt = new Intl.DateTimeFormat('fr-FR', {
  day: '2-digit',
  month: '2-digit',
  timeZone: FUSEAU,
});
const formatHeure = new Intl.DateTimeFormat('fr-FR', {
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23',
  timeZone: FUSEAU,
});

const espacesFines = (texte: string) => texte.replace(/[\s\u00a0\u202f]/g, ESPACE_FINE);

/**
 * 3278239 → « 3 278 239 » (espace fine insécable). Valeur indisponible (NaN : API absente ou source non raccordée)
 * → « 0 » (décision du 20/10/2026, docs/decisions.md).
 */
export function nf(n: number): string {
  return espacesFines(formatNombre.format(Number.isFinite(n) ? n : 0));
}

/** Ratio 0,54 → « 54,0 % ». Ratio indisponible (dénominateur nul, valeur inconnue) → « 0,0 % ». */
export function pct(ratio: number, decimales = 1): string {
  const valeur = new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  }).format(Number.isFinite(ratio) ? ratio * 100 : 0);
  return `${espacesFines(valeur)}${ESPACE_INSECABLE}%`;
}

/** Part sûre : renvoie NaN (affiché « 0,0 % ») quand le dénominateur est nul. */
export function part(numerateur: number, denominateur: number): number {
  return denominateur === 0 ? Number.NaN : numerateur / denominateur;
}

/** « 2026-01-14T11:59:00Z » → « 14/01/2026 ». */
export function dateFr(valeur: string | Date): string {
  return formatDate.format(new Date(valeur));
}

/** « 2026-01-14T11:59:00Z » → « 11h59 ». */
export function heureFr(valeur: string | Date): string {
  return formatHeure.format(new Date(valeur)).replace(':', 'h');
}

/** « 14/01/2026 à 11h59 », texte de la pastille « Dernière mise à jour ». */
export function miseAJourFr(valeur: string | Date): string {
  return `${dateFr(valeur)} à ${heureFr(valeur)}`;
}

/** Date seule « aaaa-mm-jj » de l'API, lue comme un jour du Togo (UTC+0). */
const jour = (iso: string) => new Date(`${iso}T00:00:00Z`);

/** « 2026-01-05 » → « 5 janvier » (lecture d'une semaine : « Semaine du 5 janvier »). */
export function jourMoisFr(iso: string): string {
  return formatJourMois.format(jour(iso));
}

/** « 2026-01-05 » → « 05/01 » (axe des semaines). */
export function jourMoisCourt(iso: string): string {
  return formatJourMoisCourt.format(jour(iso));
}
