import { useMemo, useState } from 'react';
import type { InscriptionsParSemaine } from '../../api/client';
import { useSemaines } from '../../api/enrolement';
import { Graphique } from '../../composants/graphique/Graphique';
import type { EChartsCoreOption } from '../../composants/graphique/echarts';
import { INCONNUE, estConnu, semainesInconnues } from '../../lib/blocsVides';
import { dateFr, jourMoisCourt, nf } from '../../lib/format';
import { jeton } from '../../lib/jetons';
import { lectureSemaine } from '../../lib/semaines';
import { usePlageApi, usePlagePeriode } from '../../lib/usePlagePeriode';

function option(donnees: InscriptionsParSemaine, active: number): EChartsCoreOption {
  const couleurs = {
    barre: jeton('--serie-1'),
    horsPeriode: jeton('--seq-1'),
    active: jeton('--seq-4'),
    courbe: jeton('--bleu'),
    texte: jeton('--encre-2'),
    trait: jeton('--trait'),
  };
  const valeur = (n: number) => (estConnu(n) ? n : null);
  const connu = donnees.semaines.some((s) => estConnu(s.inscriptions));
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
      // Échelle fictive sans chiffres, pour garder les lignes de la grille.
      ...(connu ? {} : { min: 0, max: 4, interval: 1 }),
      // Sans chiffres, l'échelle n'aurait aucun sens : on garde la grille, sans graduations.
      axisLabel: { show: connu, color: couleurs.texte, fontSize: 12, formatter: (v: number) => nf(v) },
      splitLine: { lineStyle: { color: couleurs.trait } },
    },
    series: [
      {
        name: 'Inscriptions',
        type: 'bar',
        barMaxWidth: 28,
        data: donnees.semaines.map((s, i) => ({
          value: valeur(s.inscriptions),
          itemStyle: {
            color: i === active ? couleurs.active : s.dansLaPeriode ? couleurs.barre : couleurs.horsPeriode,
            borderRadius: [3, 3, 0, 0],
          },
        })),
        emphasis: { disabled: true },
      },
      {
        name: 'NIU générés',
        type: 'line',
        data: donnees.semaines.map((s) => valeur(s.niuGeneres)),
        symbol: 'circle',
        symbolSize: (_v: number, p: { dataIndex: number }) => (p.dataIndex === active ? 9 : 0),
        lineStyle: { color: couleurs.courbe, width: 2 },
        itemStyle: { color: couleurs.courbe, borderColor: jeton('--surface'), borderWidth: 2 },
        emphasis: { disabled: true },
      },
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
  const { donnees } = usePlagePeriode('enrolement');
  const requete = useSemaines(plage, prete);
  const { isPending } = requete;
  const [survol, setSurvol] = useState<number | null>(null);

  // Sans réponse de l'API : les 12 semaines attendues, sans chiffres (fin de période, dernière donnée ou aujourd'hui).
  const fin = plage?.au ?? donnees?.au ?? new Date().toISOString().slice(0, 10);
  const data = useMemo(() => {
    const d = requete.data ?? semainesInconnues(fin);
    // NIU par date de génération pas encore alimentés : affichés à 0, sans courbe (décision du 20/10/2026).
    return d.niuDisponibles ? d : { ...d, semaines: d.semaines.map((s) => ({ ...s, niuGeneres: INCONNUE })) };
  }, [requete.data, fin]);
  const semaines = data.semaines;
  const derniere = semaines.length - 1;
  const active = survol !== null && survol <= derniere ? survol : derniere;
  const graphique = useMemo(() => option(data, active), [data, active]);

  return (
    <section className="panneau bloc-semaines" aria-labelledby="titre-semaines">
      <div className="bloc__entete">
        <div>
          <div className="bloc__titre">
            <h2 id="titre-semaines" className="titre-bloc">
              Inscriptions et NIU par semaine
            </h2>
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
          <li>
            <i className="legende__courbe" aria-hidden="true" />
            NIU générés
          </li>
        </ul>
      </div>

      {isPending && <p className="texte-2 etat-chargement">Chargement des chiffres…</p>}
      {semaines.length === 0 && <p className="texte-2">Aucune inscription pour le moment.</p>}

      {semaines.length > 0 && (
        <>
          <p className="lecture" aria-live="polite">
            {lectureSemaine(semaines[active])}
          </p>
          <Graphique
            option={graphique}
            hauteur={260}
            libelle={`Inscriptions et NIU générés par semaine, du ${dateFr(semaines[0].lundi)} au ${dateFr(semaines[derniere].lundi)}`}
            onSurvol={(c) => setSurvol(c?.indice ?? null)}
            onClic={(c) => setSurvol(c.indice ?? null)}
          />
          <details className="equivalent">
            <summary>Voir le tableau des 12 semaines</summary>
            <table className="tableau">
              <caption className="visuellement-cache">Inscriptions et NIU générés par semaine</caption>
              <thead>
                <tr>
                  <th scope="col">Semaine du</th>
                  <th scope="col">Inscriptions</th>
                  <th scope="col">NIU générés</th>
                </tr>
              </thead>
              <tbody>
                {semaines.map((s) => (
                  <tr key={s.lundi} className={s.dansLaPeriode ? undefined : 'hors-periode'}>
                    <th scope="row">{dateFr(s.lundi)}</th>
                    <td className="chiffre">{nf(s.inscriptions)}</td>
                    <td className="chiffre">{nf(s.niuGeneres)}</td>
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
