import { useMemo, useState } from 'react';
import { Tab, TabList, TabPanel, Tabs } from 'react-aria-components';
import type { JourInscriptions } from '../../api/client';
import { useJours } from '../../api/enrolement';
import { Chevron } from '../../composants/blocs/Icone';
import { Graphique } from '../../composants/graphique/Graphique';
import type { EChartsCoreOption } from '../../composants/graphique/echarts';
import { estConnu } from '../../lib/blocsVides';
import { dateFr, nf } from '../../lib/format';
import { eclaircir, jeton } from '../../lib/jetons';
import {
  NOMBRE_PAGES,
  aujourdhuiTogo,
  joursInconnus,
  lectureJours,
  libelleJour,
  pageDeJours,
  totauxJours,
} from '../../lib/jours';

type Vue = 'graphique' | 'tableau';

/** Deux barres par jour (inscriptions, NIU générés), valeur au-dessus ; le jour en cours plus clair, en pointillé. */
function option(jours: JourInscriptions[], aujourdhui: string): EChartsCoreOption {
  const couleurs = {
    inscriptions: jeton('--serie-1'),
    niu: jeton('--statut-niu'),
    encre: jeton('--encre'),
    texte: jeton('--encre-2'),
    bleu: jeton('--bleu'),
    trait: jeton('--trait'),
  };
  const serie = (nom: string, couleur: string, valeur: (j: JourInscriptions) => number) => ({
    name: nom,
    type: 'bar',
    barMaxWidth: 26,
    barGap: '12%',
    data: jours.map((j) => ({
      value: estConnu(valeur(j)) ? valeur(j) : null,
      // Jour en cours : barre plus claire au contour pointillé ; son étiquette garde la couleur du texte.
      itemStyle:
        j.jour === aujourdhui
          ? {
              color: eclaircir(couleur, 0.6),
              borderColor: couleur,
              borderWidth: 1.5,
              borderType: 'dashed',
              borderRadius: [3, 3, 0, 0],
            }
          : { color: couleur, borderRadius: [3, 3, 0, 0] },
    })),
    label: {
      show: true,
      position: 'top',
      color: couleurs.encre,
      fontSize: 11,
      formatter: (p: { value: number | null }) => (p.value == null ? '' : nf(p.value)),
    },
    emphasis: { disabled: true },
  });
  return {
    animation: false,
    grid: { left: 4, right: 4, top: 24, bottom: 4, containLabel: true },
    textStyle: { fontFamily: jeton('--police') || undefined },
    tooltip: { show: false },
    xAxis: {
      type: 'category',
      data: jours.map((j) =>
        j.jour === aujourdhui ? `${libelleJour(j.jour)}\naujourd’hui` : libelleJour(j.jour),
      ),
      axisTick: { show: false },
      axisLine: { lineStyle: { color: couleurs.trait } },
      axisLabel: { color: couleurs.texte, fontSize: 12, interval: 0, lineHeight: 16 },
    },
    // Les valeurs sont écrites sur les barres : l'axe vertical ne garde que la grille.
    yAxis: { type: 'value', axisLabel: { show: false }, splitLine: { lineStyle: { color: couleurs.trait } } },
    series: [
      serie('Inscriptions', couleurs.inscriptions, (j) => j.inscriptions),
      serie('NIU générés', couleurs.niu, (j) => j.niuGeneres),
    ],
  };
}

/**
 * Bloc « Inscriptions et NIU par jour » (décision du 29/10/2026) : aujourd'hui et les 6 jours précédents, puis, page
 * par page, jusqu'à trois semaines en arrière (GET /enrolement/jours, relu toutes les 30 s). Inscriptions au jour de
 * réception, NIU au jour de génération. Onglets Graphique (deux barres par jour, valeur au-dessus) et Tableau. National,
 * sans période : il suit la date du jour. Sans réponse de l'API : les 7 jours, chiffres à 0, barres vides.
 */
export function BlocJours() {
  const requete = useJours();
  const [vue, setVue] = useState<Vue>('graphique');
  const [page, setPage] = useState(0);
  const donnees = requete.data ?? joursInconnus(aujourdhuiTogo());
  const aujourdhui = donnees.aujourdhui;
  const jours = useMemo(() => pageDeJours(donnees, page), [donnees, page]);
  const graphique = useMemo(() => option(jours, aujourdhui), [jours, aujourdhui]);
  const totaux = totauxJours(jours);
  const premier = jours[0]?.jour;
  const dernier = jours[jours.length - 1]?.jour;

  return (
    <section className="panneau bloc-jours" aria-labelledby="titre-jours">
      <Tabs selectedKey={vue} onSelectionChange={(cle) => setVue(cle as Vue)}>
        <div className="bloc__entete">
          <div className="bloc__titre">
            <h2 id="titre-jours" className="titre-bloc">
              Inscriptions et NIU par jour
            </h2>
          </div>
          <TabList aria-label="Affichage" className="onglets">
            <Tab id="graphique" className="onglets__onglet">
              Graphique
            </Tab>
            <Tab id="tableau" className="onglets__onglet">
              Tableau
            </Tab>
          </TabList>
        </div>

        {requete.isPending && <p className="texte-2 etat-chargement">Chargement des chiffres…</p>}

        <div className="bloc-jours__barre">
          <p className="lecture" aria-live="polite">
            {lectureJours(jours)}
            {page === 0 && ' (jusqu’à aujourd’hui)'}
          </p>
          <nav className="bloc-jours__nav" aria-label="Semaines">
            <button
              type="button"
              className="pagination__bouton"
              aria-label="Semaine précédente"
              disabled={page === NOMBRE_PAGES - 1}
              onClick={() => setPage(page + 1)}
            >
              <Chevron gauche taille={12} />
            </button>
            <span className="bloc-jours__points" aria-hidden="true">
              {Array.from({ length: NOMBRE_PAGES }, (_, i) => NOMBRE_PAGES - 1 - i).map((p) => (
                <i key={p} className={p === page ? 'actif' : undefined} />
              ))}
            </span>
            <button
              type="button"
              className="pagination__bouton"
              aria-label="Semaine suivante"
              disabled={page === 0}
              onClick={() => setPage(page - 1)}
            >
              <Chevron taille={12} />
            </button>
          </nav>
        </div>

        <TabPanel id="graphique" className="onglets__panneau">
          <ul className="legende" aria-label="Légende">
            <li>
              <i className="legende__barre" aria-hidden="true" />
              Inscriptions
            </li>
            <li>
              <i className="legende__barre legende__barre--niu" aria-hidden="true" />
              NIU générés
            </li>
          </ul>
          {premier && dernier && (
            <Graphique
              option={graphique}
              hauteur={280}
              libelle={`Inscriptions et NIU générés par jour, du ${dateFr(premier)} au ${dateFr(dernier)}`}
            />
          )}
        </TabPanel>
        <TabPanel id="tableau" className="onglets__panneau">
          <table className="tableau">
            <caption className="visuellement-cache">Inscriptions et NIU générés par jour</caption>
            <thead>
              <tr>
                <th scope="col">Jour</th>
                <th scope="col">Inscriptions</th>
                <th scope="col">NIU générés</th>
              </tr>
            </thead>
            <tbody>
              {jours.map((j) => (
                <tr key={j.jour} className={j.jour === aujourdhui ? 'bloc-jours__aujourdhui' : undefined}>
                  <th scope="row">
                    {libelleJour(j.jour)}
                    {j.jour === aujourdhui && ' (aujourd’hui)'}
                  </th>
                  <td className="chiffre">{nf(j.inscriptions)}</td>
                  <td className="chiffre">{nf(j.niuGeneres)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <th scope="row">Total</th>
                <td className="chiffre">{nf(totaux.inscriptions)}</td>
                <td className="chiffre">{nf(totaux.niuGeneres)}</td>
              </tr>
            </tfoot>
          </table>
        </TabPanel>
      </Tabs>
    </section>
  );
}
