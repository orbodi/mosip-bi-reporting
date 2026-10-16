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
const formatHeure = new Intl.DateTimeFormat('fr-FR', {
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23',
  timeZone: FUSEAU,
});

const espacesFines = (texte: string) => texte.replace(/[\s\u00a0\u202f]/g, ESPACE_FINE);

/** 3278239 → « 3 278 239 » (espace fine insécable). */
export function nf(n: number): string {
  if (!Number.isFinite(n)) return '–';
  return espacesFines(formatNombre.format(n));
}

/** Ratio 0,54 → « 54,0 % ». Renvoie « – » si le dénominateur était nul. */
export function pct(ratio: number, decimales = 1): string {
  if (!Number.isFinite(ratio)) return '–';
  const valeur = new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  }).format(ratio * 100);
  return `${espacesFines(valeur)}${ESPACE_INSECABLE}%`;
}

/** Part sûre : renvoie NaN (affiché « – ») quand le dénominateur est nul. */
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
