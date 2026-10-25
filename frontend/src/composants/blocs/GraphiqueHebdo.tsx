import { useMemo, useState } from 'react';
import type { SemaineValeurs } from '../../lib/blocsVides';
import { dateFr, dimanche, etiquetteVisible, nf, semaineCourte, semaineDates } from '../../lib/format';
import { jeton } from '../../lib/jetons';
import { Graphique } from '../graphique/Graphique';
import type { EChartsCoreOption } from '../graphique/echarts';
import { JETON_COULEUR, type Couleur } from './couleurs';

export type { SemaineValeurs } from '../../lib/blocsVides';

export interface SerieHebdo {
  cle: string;
  libelle: string;
  couleur: Couleur;
  /** barre : barres côte à côte ; pile : barres empilées ; courbe : ligne. */
  type: 'barre' | 'pile' | 'courbe';
}

interface Props {
  semaines: SemaineValeurs[];
  series: SerieHebdo[];
  /** Phrase de lecture d'une semaine (au survol ; la dernière par défaut). */
  lecture: (s: SemaineValeurs) => string;
  /** Description du graphique (role="img") et légende du tableau équivalent. */
  libelle: string;
  hauteur?: number;
  ton?: 'bleu' | 'rouge';
  /** Étiquettes de mois plutôt que de semaines. */
  axeMois?: boolean;
}

const MOIS = [
  'janv.',
  'févr.',
  'mars',
  'avr.',
  'mai',
  'juin',
  'juil.',
  'août',
  'sept.',
  'oct.',
  'nov.',
  'déc.',
];

/**
 * Graphique hebdomadaire de la maquette (barres simples ou empilées, courbe) avec lecture de la semaine survolée et
 * tableau équivalent. Valeurs inconnues (NaN) : semaine sans barre, échelle sans graduations.
 */
export function GraphiqueHebdo({
  semaines,
  series,
  lecture,
  libelle,
  hauteur = 240,
  ton = 'bleu',
  axeMois,
}: Props) {
  const [survol, setSurvol] = useState<number | null>(null);
  const derniere = semaines.length - 1;
  const active = survol !== null && survol <= derniere ? survol : derniere;

  const option = useMemo<EChartsCoreOption>(() => {
    const connu = semaines.some((s) => series.some((x) => Number.isFinite(s.valeurs[x.cle])));
    const valeur = (n: number | undefined) => (n !== undefined && Number.isFinite(n) ? n : null);
    const texte = jeton('--encre-2');
    const trait = jeton('--trait');
    const etiquette = (lundi: string, i: number) => {
      if (!axeMois) return semaineCourte(lundi);
      const mois = (l: string) => new Date(`${l}T00:00:00Z`).getUTCMonth();
      return i === 0 || mois(lundi) !== mois(semaines[i - 1].lundi) ? MOIS[mois(lundi)] : '';
    };
    return {
      animation: false,
      grid: { left: 8, right: 8, top: 16, bottom: 8, containLabel: true },
      textStyle: { fontFamily: jeton('--police') || undefined },
      tooltip: { show: false },
      xAxis: {
        type: 'category',
        data: semaines.map((s, i) => etiquette(s.lundi, i)),
        axisTick: { show: false },
        axisLine: { lineStyle: { color: trait } },
        // Semaines : une étiquette sur deux au-delà de 8, la plus récente toujours visible. Mois : chaque début de mois.
        axisLabel: {
          color: texte,
          fontSize: 12,
          interval: axeMois ? 0 : etiquetteVisible(semaines.length, semaines.length > 8 ? 2 : 1),
          hideOverlap: axeMois,
        },
      },
      yAxis: {
        type: 'value',
        ...(connu ? {} : { min: 0, max: 4, interval: 1 }),
        axisLabel: { show: connu, color: texte, fontSize: 12, formatter: (v: number) => nf(v) },
        splitLine: { lineStyle: { color: trait } },
      },
      series: series.map((x) => {
        const couleur = jeton(JETON_COULEUR[x.couleur]);
        if (x.type === 'courbe') {
          return {
            name: x.libelle,
            type: 'line',
            data: semaines.map((s) => valeur(s.valeurs[x.cle])),
            symbol: 'circle',
            symbolSize: (_v: number, p: { dataIndex: number }) => (p.dataIndex === active ? 9 : 0),
            lineStyle: { color: couleur, width: 2 },
            itemStyle: { color: couleur, borderColor: jeton('--surface'), borderWidth: 2 },
            emphasis: { disabled: true },
          };
        }
        return {
          name: x.libelle,
          type: 'bar',
          stack: x.type === 'pile' ? 'pile' : undefined,
          barMaxWidth: 28,
          data: semaines.map((s, i) => ({
            value: valeur(s.valeurs[x.cle]),
            itemStyle: { color: couleur, opacity: i === active ? 1 : 0.85 },
          })),
          emphasis: { disabled: true },
        };
      }),
    };
  }, [semaines, series, active, axeMois]);

  if (semaines.length === 0) return <p className="texte-2">Aucune semaine sur la période.</p>;

  return (
    <div className="graphique-hebdo">
      <p className={`lecture${ton === 'rouge' ? ' lecture--rouge' : ''}`} aria-live="polite">
        {lecture(semaines[active])}
      </p>
      <Graphique
        option={option}
        hauteur={hauteur}
        libelle={`${libelle}, du ${dateFr(semaines[0].lundi)} au ${dateFr(dimanche(semaines[derniere].lundi))}`}
        onSurvol={(c) => setSurvol(c?.indice ?? null)}
        onClic={(c) => setSurvol(c.indice ?? null)}
      />
      <details className="equivalent">
        <summary>Voir le tableau des semaines</summary>
        <table className="tableau">
          <caption className="visuellement-cache">{libelle}</caption>
          <thead>
            <tr>
              <th scope="col">Semaine</th>
              {series.map((x) => (
                <th key={x.cle} scope="col">
                  {x.libelle}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {semaines.map((s) => (
              <tr key={s.lundi}>
                <th scope="row">{semaineDates(s.lundi)}</th>
                {series.map((x) => (
                  <td key={x.cle} className="chiffre">
                    {nf(s.valeurs[x.cle] ?? Number.NaN)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
