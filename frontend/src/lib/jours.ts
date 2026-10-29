import type { InscriptionsParJour, JourInscriptions } from '../api/client';
import { INCONNUE } from './blocsVides';
import { jourMoisFr, nf } from './format';

/** Jours par page du bloc « Inscriptions et NIU par jour » : aujourd'hui et les 6 jours précédents. */
export const JOURS_PAR_PAGE = 7;
/** Pages disponibles : la semaine en cours et trois semaines en arrière (28 jours, GET /enrolement/jours). */
export const NOMBRE_PAGES = 4;

const JOURS_SEMAINE = ['dim.', 'lun.', 'mar.', 'mer.', 'jeu.', 'ven.', 'sam.'];
const date = (iso: string) => new Date(`${iso}T00:00:00Z`);
const iso = (d: Date) => d.toISOString().slice(0, 10);

/** Date du jour au Togo (UTC+0), « 2026-10-29 ». */
export function aujourdhuiTogo(maintenant = new Date()): string {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Africa/Lome' }).format(maintenant);
}

/** Sans réponse de l'API : les 28 jours attendus jusqu'à aujourd'hui, chiffres inconnus (affichés 0, sans barre). */
export function joursInconnus(aujourdhui: string): InscriptionsParJour {
  const fin = date(aujourdhui);
  const jours: JourInscriptions[] = Array.from({ length: JOURS_PAR_PAGE * NOMBRE_PAGES }, (_, i) => {
    const d = new Date(fin);
    d.setUTCDate(fin.getUTCDate() - (JOURS_PAR_PAGE * NOMBRE_PAGES - 1 - i));
    return { jour: iso(d), inscriptions: INCONNUE, niuGeneres: INCONNUE };
  });
  return { perimetre: 'Ensemble du Togo', aujourdhui, niuDisponibles: true, jours };
}

/**
 * Les 7 jours d'une page, du plus ancien au plus récent : page 0 = aujourd'hui et les 6 jours précédents, page 1 = la
 * semaine d'avant, jusqu'à la page 3. NIU inconnus tant que leur source n'est pas alimentée (affichés 0).
 */
export function pageDeJours(donnees: InscriptionsParJour, page: number): JourInscriptions[] {
  const fin = donnees.jours.length - page * JOURS_PAR_PAGE;
  const jours = donnees.jours.slice(Math.max(0, fin - JOURS_PAR_PAGE), Math.max(0, fin));
  return donnees.niuDisponibles ? jours : jours.map((j) => ({ ...j, niuGeneres: INCONNUE }));
}

/** « 2026-10-29 » → « jeu. 29/10 ». */
export function libelleJour(jour: string): string {
  const d = date(jour);
  const jj = String(d.getUTCDate()).padStart(2, '0');
  const mm = String(d.getUTCMonth() + 1).padStart(2, '0');
  return `${JOURS_SEMAINE[d.getUTCDay()]} ${jj}/${mm}`;
}

const jourDuMois = (jour: string) => {
  const j = date(jour).getUTCDate();
  return j === 1 ? '1er' : String(j);
};

/** « 1er janvier », « 29 octobre ». */
const jourEtMois = (jour: string) => jourMoisFr(jour).replace(/^\d+/, jourDuMois(jour));

/** « Du 23 au 29 octobre », « Du 30 septembre au 6 octobre ». */
export function intervalleJours(premier: string, dernier: string): string {
  const memeMois = premier.slice(0, 7) === dernier.slice(0, 7);
  return `Du ${memeMois ? jourDuMois(premier) : jourEtMois(premier)} au ${jourEtMois(dernier)}`;
}

const somme = (valeurs: number[]) =>
  valeurs.some((v) => Number.isFinite(v))
    ? valeurs.reduce((s, v) => s + (Number.isFinite(v) ? v : 0), 0)
    : INCONNUE;

/** Totaux d'une page (inconnus si aucun jour n'est connu). */
export function totauxJours(jours: JourInscriptions[]): { inscriptions: number; niuGeneres: number } {
  return {
    inscriptions: somme(jours.map((j) => j.inscriptions)),
    niuGeneres: somme(jours.map((j) => j.niuGeneres)),
  };
}

/** « Du 8 au 14 janvier : 4 600 inscriptions, 2 900 NIU générés » (lecture de la page affichée). */
export function lectureJours(jours: JourInscriptions[]): string {
  if (jours.length === 0) return '';
  const t = totauxJours(jours);
  return `${intervalleJours(jours[0].jour, jours[jours.length - 1].jour)} : ${nf(t.inscriptions)} inscriptions, ${nf(t.niuGeneres)} NIU générés`;
}
