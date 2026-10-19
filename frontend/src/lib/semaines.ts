import type { Semaine } from '../api/client';
import { jourMoisFr, nf, part, pct } from './format';

/** Lecture d'une semaine (maquette) : « Semaine du 5 janvier : 20 230 inscriptions, 17 626 NIU générés (87,1 %). » */
export function lectureSemaine(s: Semaine, niuDisponibles: boolean): string {
  if (!Number.isFinite(s.inscriptions)) return `Semaine du ${jourMoisFr(s.lundi)} : chiffres indisponibles.`;
  const debut = `Semaine du ${jourMoisFr(s.lundi)} : ${nf(s.inscriptions)} inscriptions`;
  if (!niuDisponibles) return `${debut}.`;
  return `${debut}, ${nf(s.niuGeneres)} NIU générés (${pct(part(s.niuGeneres, s.inscriptions))}).`;
}
