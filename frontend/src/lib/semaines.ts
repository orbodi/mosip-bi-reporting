import type { Semaine } from '../api/client';
import { jourMoisFr, nf, part, pct } from './format';

/**
 * Lecture d'une semaine (maquette) : « Semaine du 5 janvier : 20 230 inscriptions, 17 626 NIU générés (87,1 %). »
 * Chiffres indisponibles : 0 (lib/format.ts).
 */
export function lectureSemaine(s: Semaine): string {
  return `Semaine du ${jourMoisFr(s.lundi)} : ${nf(s.inscriptions)} inscriptions, ${nf(s.niuGeneres)} NIU générés (${pct(part(s.niuGeneres, s.inscriptions))}).`;
}
