import { useMemo, useState } from 'react';
import type { InscriptionsParSemaine } from '../../api/client';
import { useSemaines } from '../../api/enrolement';
import { Graphique } from '../../composants/graphique/Graphique';
import type { EChartsCoreOption } from '../../composants/graphique/echarts';
import { dateFr, jourMoisCourt, nf } from '../../lib/format';
import { jeton } from '../../lib/jetons';
import { lectureSemaine } from '../../lib/semaines';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import { usePlageApi } from '../../lib/usePlagePeriode';
import { PastillePortee } from './PastillePortee';

function option(donnees: InscriptionsParSemaine, active: number): EChartsCoreOption {
  const couleurs = {
    barre: jeton('--serie-1'),
    horsPeriode: jeton('--seq-1'),
    active: jeton('--seq-4'),
    courbe: jeton('--bleu'),
    texte: jeton('--encre-2'),
    trait: jeton('--trait'),
  };
  return {
    animation: false,
    grid: { left: 8, right: 8, top: 16, bottom: 8, containLabel: true },
    textStyle: { fontFamily: jeton('--police') || undefined },
    tooltip: { show: false },
    xAxis: {
      type: 'category',
      data: donnees.semaines.map((s) => jourMoisCourt(s.lundi)),
      axisTick: { show: false },
      axisLine: { lineStyle: { color: couleurs.trait } },
      axisLabel: { color: couleurs.texte, fontSize: 12, interval: 0, hideOverlap: true },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: couleurs.texte, fontSize: 12, formatter: (v: number) => nf(v) },
      splitLine: { lineStyle: { color: couleurs.trait } },
    },
    series: [
      {
        name: 'Inscriptions',
        type: 'bar',
        barMaxWidth: 28,
        data: donnees.semaines.map((s, i) => ({
          value: s.inscriptions,
          itemStyle: {
            color: i === active ? couleurs.active : s.dansLaPeriode ? couleurs.barre : couleurs.horsPeriode,
            borderRadius: [3, 3, 0, 0],
          },
        })),
        emphasis: { disabled: true },
      },
      ...(donnees.niuDisponibles
        ? [
            {
              name: 'NIU générés',
              type: 'line',
              data: donnees.semaines.map((s) => s.niuGeneres),
              symbol: 'circle',
              symbolSize: (_v: number, p: { dataIndex: number }) => (p.dataIndex === active ? 9 : 0),
              lineStyle: { color: couleurs.courbe, width: 2 },
              itemStyle: { color: couleurs.courbe, borderColor: jeton('--surface'), borderWidth: 2 },
              emphasis: { disabled: true },
            },
          ]
        : []),
    ],
  };
}

/**
 * Bloc « Inscriptions et NIU par semaine » : 12 semaines complètes, inscriptions en barres (jour de réception) et
 * NIU générés en courbe (jour de génération). Ne suit pas le filtre Région (décision P3 de docs/plans/enrolement.md).
 * Lecture d'une semaine au survol ; tableau équivalent pour le clavier et les lecteurs d'écran.
 */
export function BlocSemaines() {
  const { plage, prete, choix } = usePlageApi('enrolement');
  const { actif } = useFiltreRegion();
  const { data, isPending, isError } = useSemaines(plage, prete);
  const [survol, setSurvol] = useState<number | null>(null);

  const semaines = data?.semaines ?? [];
  const derniere = semaines.length - 1;
  const active = survol !== null && survol <= derniere ? survol : derniere;
  const graphique = useMemo(() => (data ? option(data, active) : undefined), [data, active]);

  return (
    <section className="panneau bloc-semaines" aria-labelledby="titre-semaines">
      <div className="bloc__entete">
        <div>
          <div className="bloc__titre">
            <h2 id="titre-semaines" className="titre-bloc">
              Inscriptions et NIU par semaine
            </h2>
            {actif && <PastillePortee perimetre={data?.perimetre} />}
          </div>
          <p className="texte-2 bloc__sous-titre">
            {choix === 'tout'
              ? '12 dernières semaines complètes.'
              : '12 semaines complètes jusqu’à la fin de la période ; en clair, les semaines hors période.'}
          </p>
        </div>
        <ul className="legende" aria-label="Légende">
          <li>
            <i className="legende__barre" aria-hidden="true" />
            Inscriptions
          </li>
          {data?.niuDisponibles !== false && (
            <li>
              <i className="legende__courbe" aria-hidden="true" />
              NIU générés
            </li>
          )}
        </ul>
      </div>

      {isPending && <p className="texte-2">Chargement des chiffres…</p>}
      {isError && (
        <p role="alert" className="alerte-donnees">
          Chiffres indisponibles pour le moment. Ils réapparaîtront dès que l’API répondra.
        </p>
      )}
      {data && semaines.length === 0 && <p className="texte-2">Aucune inscription pour le moment.</p>}

      {data && semaines.length > 0 && graphique && (
        <>
          <p className="lecture" aria-live="polite">
            {lectureSemaine(semaines[active], data.niuDisponibles)}
          </p>
          <Graphique
            option={graphique}
            hauteur={260}
            libelle={`Inscriptions${data.niuDisponibles ? ' et NIU générés' : ''} par semaine, du ${dateFr(semaines[0].lundi)} au ${dateFr(semaines[derniere].lundi)}`}
            onSurvol={(c) => setSurvol(c?.indice ?? null)}
            onClic={(c) => setSurvol(c.indice ?? null)}
          />
          {!data.niuDisponibles && (
            <p className="alerte-donnees" role="note">
              NIU par date de génération : source pas encore alimentée. La courbe s’affichera quand le
              pipeline la remplira (règle à valider avec l’équipe MOSIP).
            </p>
          )}
          <details className="equivalent">
            <summary>Voir le tableau des 12 semaines</summary>
            <table className="tableau">
              <caption className="visuellement-cache">Inscriptions et NIU générés par semaine</caption>
              <thead>
                <tr>
                  <th scope="col">Semaine du</th>
                  <th scope="col">Inscriptions</th>
                  {data.niuDisponibles && <th scope="col">NIU générés</th>}
                </tr>
              </thead>
              <tbody>
                {semaines.map((s) => (
                  <tr key={s.lundi} className={s.dansLaPeriode ? undefined : 'hors-periode'}>
                    <th scope="row">{dateFr(s.lundi)}</th>
                    <td className="chiffre">{nf(s.inscriptions)}</td>
                    {data.niuDisponibles && <td className="chiffre">{nf(s.niuGeneres)}</td>}
                  </tr>
                ))}
              </tbody>
            </table>
          </details>
        </>
      )}
    </section>
  );
}
