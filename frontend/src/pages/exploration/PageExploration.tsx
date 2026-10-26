import { useState } from 'react';
import { Tab, TabList, TabPanel, Tabs } from 'react-aria-components';
import type { LigneZone, Territoire } from '../../api/client';
import { useTerritoire } from '../../api/enrolement';
import { useMeta } from '../../api/meta';
import { ChampChoix, type OptionChoix } from '../../composants/blocs/ChampChoix';
import { Chevron } from '../../composants/blocs/Icone';
import { GrandChiffre } from '../../composants/blocs/Indicateur';
import { Pagination } from '../../composants/blocs/Pagination';
import { Panneau } from '../../composants/blocs/Panneau';
import { Bandeau } from '../../composants/coque/Bandeau';
import { nf, part, pct } from '../../lib/format';
import { paginer, type TaillePage } from '../../lib/pagination';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import type { DefinitionPage } from '../pages';
import {
  DIMENSIONS,
  NIVEAUX_TERRITOIRE,
  NOMBRE_INDICATEURS,
  SOURCES,
  type CleDimension,
  type SourceExploration,
} from './catalogue';
import './exploration.css';

type Mode = 'n' | 'pt' | 'pf';

/** Texte des niveaux de territoire désactivés (maquette) : chaque niveau attend le choix du niveau au-dessus. */
const VIDE_TERRITOIRE = [
  'Toutes',
  'Choisir la région',
  'Choisir la préfecture',
  'Choisir la commune',
  'Choisir le canton',
  'Choisir la localité',
];
/** Libellé « toutes les zones » de chaque niveau (région, préfecture, commune : Toutes ; canton, centre : Tous). */
const TOUTES_ZONES = ['Toutes', 'Toutes', 'Toutes', 'Tous', 'Toutes', 'Tous'];
const MOIS_COURT = [
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
const moisCourt = (m: string) => `${MOIS_COURT[Number(m.slice(5, 7)) - 1]} ${m.slice(0, 4)}`;

const MOIS = [
  'janvier',
  'février',
  'mars',
  'avril',
  'mai',
  'juin',
  'juillet',
  'août',
  'septembre',
  'octobre',
  'novembre',
  'décembre',
];
const libelleMois = (m: string) => `${MOIS[Number(m.slice(5, 7)) - 1]} ${m.slice(0, 4)}`;

type ChampsEnrolement =
  | 'inscriptions'
  | 'niuGeneres'
  | 'enCours'
  | 'echouees'
  | 'rejetees'
  | 'preinscriptions';

/** Colonnes de l'API Territoire correspondant aux indicateurs d'enrôlement. */
const CHAMP_ENROLEMENT: Record<string, ChampsEnrolement> = {
  ins: 'inscriptions',
  niu: 'niuGeneres',
  enc: 'enCours',
  ech: 'echouees',
  rej: 'rejetees',
  pre: 'preinscriptions',
};

/** Ordre alphabétique français des listes de zones (« Éthiopie » après « Dapaong », pas à la fin). */
const ordreFr = new Intl.Collator('fr', { sensitivity: 'base' });

/**
 * Listes en cascade du territoire : pour chaque niveau sous la région, les sous-zones de la zone choisie au niveau
 * au-dessus (API Territoire, sans période : la liste ne dépend pas des chiffres). Six appels au plus, toujours dans
 * le même ordre (règle des hooks) ; un niveau dont le parent n'est pas choisi ne fait pas d'appel.
 */
function useListesTerritoire(chemin: string[]): (Territoire | undefined)[] {
  const listes = [
    useTerritoire(undefined, chemin[0], !!chemin[0]).data,
    useTerritoire(undefined, chemin[1], !!chemin[1]).data,
    useTerritoire(undefined, chemin[2], !!chemin[2]).data,
    useTerritoire(undefined, chemin[3], !!chemin[3]).data,
    useTerritoire(undefined, chemin[4], !!chemin[4]).data,
  ];
  // listes[k] : sous-zones de chemin[k], options du niveau k + 1 ; jamais celles d'une zone qui n'est plus choisie.
  return listes.map((t, k) => (t && chemin[k] && t.zone === chemin[k] ? t : undefined));
}

function moisEntre(debut: string, fin: string): string[] {
  const out: string[] = [];
  let [a, m] = [Number(debut.slice(0, 4)), Number(debut.slice(5, 7))];
  const [af, mf] = [Number(fin.slice(0, 4)), Number(fin.slice(5, 7))];
  while (a < af || (a === af && m <= mf)) {
    out.push(`${a}-${String(m).padStart(2, '0')}`);
    m += 1;
    if (m > 12) [a, m] = [a + 1, 1];
  }
  return out;
}

function plageDe(periode: string): { du: string; au: string } | undefined {
  if (periode.startsWith('A:')) return { du: `${periode.slice(2)}-01-01`, au: `${periode.slice(2)}-12-31` };
  if (periode.startsWith('M:')) {
    const [a, m] = periode.slice(2).split('-').map(Number);
    return { du: `${periode.slice(2)}-01`, au: new Date(Date.UTC(a, m, 0)).toISOString().slice(0, 10) };
  }
  return undefined;
}

/** Fichier CSV (séparateur « ; », nombres bruts) téléchargé par le navigateur. */
function telechargerCsv(nom: string, lignes: string[][]) {
  const texte = lignes
    .map((l) => l.map((c) => (/[;"\n]/.test(c) ? `"${c.replace(/"/g, '""')}"` : c)).join(';'))
    .join('\r\n');
  const url = URL.createObjectURL(new Blob(['﻿' + texte], { type: 'text/csv;charset=utf-8' }));
  const lien = document.createElement('a');
  lien.href = url;
  lien.download = nom;
  lien.click();
  URL.revokeObjectURL(url);
}

/**
 * Exploration des données (maquette/pages/Technique.dc.html) : 25 indicateurs de 5 sources, filtres, ventilation et
 * export CSV. Seule la source Enrôlement a une API : par sous-zone de la zone choisie, de la région au centre, sans
 * filtre de profil ; ailleurs le tableau garde sa forme, indicateurs à 0 (décision du 20/10/2026).
 */
export function PageExploration({ page }: { page: DefinitionPage }) {
  return (
    <>
      <Bandeau
        titre={page.titre}
        source={page.source}
        chapeau={`Les ${NOMBRE_INDICATEURS} indicateurs des cinq sources du BI : choisissez une source, filtrez, puis choisissez les indicateurs et ce qui s’affiche en lignes.`}
      />
      <div className="contenu page-m">
        <Explorateur />
      </div>
    </>
  );
}

function Explorateur() {
  const [cleSource, setCleSource] = useState<SourceExploration['cle']>('enrol');
  const source = SOURCES.find((s) => s.cle === cleSource) ?? SOURCES[0];
  const [indicateurs, setIndicateurs] = useState<string[]>([source.indicateurs[0].cle]);
  const [periode, setPeriode] = useState('tout');
  const [filtres, setFiltres] = useState<Partial<Record<CleDimension, string>>>({});
  // Zones choisies, de la région vers le centre : chemin[k] est le code choisi au niveau NIVEAUX_TERRITOIRE[k].
  const [chemin, setChemin] = useState<string[]>([]);
  const [par, setPar] = useState<string>('sous');
  const [mode, setMode] = useState<Mode>('n');
  // Pagination du tableau (beaucoup de cantons, de localités ou de mois) ; l'export CSV garde toutes les lignes.
  const [taille, setTaille] = useState<TaillePage>(20);
  const [page, setPage] = useState(0);

  const { regions } = useFiltreRegion();
  const meta = useMeta();
  const fraicheur = meta.data?.sources.find((s) => s.source === source.fraicheur);

  const choisis = source.indicateurs.filter((i) => indicateurs.includes(i.cle));
  const territoireOk = choisis.every((i) => i.territoire);
  const dimensionsSource = (Object.keys(DIMENSIONS) as CleDimension[]).filter((d) =>
    source.indicateurs.some((i) => i.dimensions.includes(d)),
  );
  const dimensionsCommunes = dimensionsSource.filter((d) => choisis.every((i) => i.dimensions.includes(d)));

  const mois =
    fraicheur?.premiereDonnee && fraicheur.derniereDonnee
      ? moisEntre(fraicheur.premiereDonnee.slice(0, 7), fraicheur.derniereDonnee.slice(0, 7))
      : [];
  const annees = [...new Set(mois.map((m) => m.slice(0, 4)))];

  const listes = useListesTerritoire(chemin);
  // Options du niveau k : régions, puis sous-zones de ce niveau dans la zone choisie au-dessus (ordre alphabétique).
  const optionsNiveau = (k: number): OptionChoix[] =>
    k === 0
      ? regions.map((r) => ({ id: r.code, libelle: r.nom }))
      : (listes[k - 1]?.lignes ?? [])
          .filter((l) => l.niveau === NIVEAUX_TERRITOIRE[k].cle && !l.horsReferentiel)
          .map((l) => ({ id: l.code, libelle: l.nom }))
          .sort((a, b) => ordreFr.compare(a.libelle, b.libelle));
  const nomDe = (k: number) => optionsNiveau(k).find((o) => o.id === chemin[k])?.libelle ?? chemin[k];
  const zoneChoisie = chemin.at(-1);
  const niveauSuivant = NIVEAUX_TERRITOIRE[chemin.length];
  const choisirNiveau = (k: number, code: string) =>
    setChemin(code ? [...chemin.slice(0, k), code] : chemin.slice(0, k));

  const optionsPar: OptionChoix[] = [
    ...(territoireOk && niveauSuivant ? [{ id: 'sous', libelle: niveauSuivant.libelle }] : []),
    ...(!periode.startsWith('A:') && !periode.startsWith('M:') ? [{ id: 'annee', libelle: 'Année' }] : []),
    ...(!periode.startsWith('M:') ? [{ id: 'mois', libelle: 'Mois' }] : []),
    ...dimensionsCommunes
      .filter((d) => !filtres[d] && DIMENSIONS[d].valeurs.length)
      .map((d) => ({ id: d, libelle: DIMENSIONS[d].libelle })),
    { id: 'total', libelle: 'Total seul' },
  ];
  const parEffectif = optionsPar.some((o) => o.id === par) ? par : optionsPar[0].id;
  const modeEffectif: Mode = mode === 'pf' && choisis.length < 2 ? 'n' : mode;

  const nomsChemin = chemin.map((_, k) => nomDe(k));
  const plage = plageDe(periode);
  // Données réelles : Enrôlement, sans filtre de profil ni de type, par sous-zone de la zone choisie, ou total.
  const reel =
    cleSource === 'enrol' &&
    Object.values(filtres).every((v) => !v) &&
    (parEffectif === 'sous' || parEffectif === 'total');
  const territoire = useTerritoire(plage, zoneChoisie, reel);
  const lignesApi = reel ? territoire.data?.lignes.filter((l) => !l.horsReferentiel) : undefined;

  const valeursDe = (l?: Pick<LigneZone, ChampsEnrolement>) =>
    choisis.map((i) => (l && CHAMP_ENROLEMENT[i.cle] ? l[CHAMP_ENROLEMENT[i.cle]] : Number.NaN));
  // On ouvre une sous-zone du niveau attendu qui a elle-même des sous-zones (pas un centre rattaché plus haut).
  const ouvrable = (l: LigneZone) =>
    !!niveauSuivant &&
    l.niveau === niveauSuivant.cle &&
    !!NIVEAUX_TERRITOIRE[chemin.length + 1] &&
    (l.ouvrable ?? l.niveau !== 'centre');

  const lignes = ((): { id: string; libelle: string; valeurs: number[]; ouvrable?: boolean }[] => {
    if (parEffectif === 'total') return [];
    if (lignesApi && parEffectif === 'sous') {
      return lignesApi.map((l) => ({
        id: l.code,
        libelle: l.nom,
        valeurs: valeursDe(l),
        ouvrable: ouvrable(l),
      }));
    }
    const inconnues = () => choisis.map(() => Number.NaN);
    if (parEffectif === 'sous') {
      return optionsNiveau(chemin.length).map((o) => ({
        id: o.id,
        libelle: o.libelle,
        valeurs: inconnues(),
        ouvrable: !!NIVEAUX_TERRITOIRE[chemin.length + 1],
      }));
    }
    if (parEffectif === 'annee') return annees.map((a) => ({ id: a, libelle: a, valeurs: inconnues() }));
    if (parEffectif === 'mois') {
      const liste = periode.startsWith('A:') ? mois.filter((m) => m.startsWith(periode.slice(2))) : mois;
      return liste.map((m) => ({ id: m, libelle: libelleMois(m), valeurs: inconnues() }));
    }
    const dim = DIMENSIONS[parEffectif as CleDimension];
    return dim ? dim.valeurs.map((v) => ({ id: v, libelle: v, valeurs: inconnues() })) : [];
  })();

  const totaux = reel && territoire.data ? valeursDe(territoire.data) : choisis.map(() => Number.NaN);
  // La page revient à 1 quand les lignes changent (autre zone, autre ventilation) : clé des lignes affichées.
  const cleLignes = `${cleSource}|${parEffectif}|${chemin.join('/')}|${periode}`;
  const [clePage, setClePage] = useState(cleLignes);
  const tranche = paginer(lignes, clePage === cleLignes ? page : 0, taille);
  const allerPage = (p: number) => {
    setClePage(cleLignes);
    setPage(p);
  };

  const cellule = (v: number, j: number, ligne: number[]) => {
    if (modeEffectif === 'pt') return pct(part(v, totaux[j]));
    if (modeEffectif === 'pf' && j > 0) return pct(part(v, ligne[0]));
    return nf(v);
  };

  const libellePar = optionsPar.find((o) => o.id === parEffectif)?.libelle ?? '';
  const titreResultat = `${choisis.map((i) => i.libelle).join(', ')}${parEffectif !== 'total' ? ` par ${libellePar.toLowerCase()}` : ''}`;
  const filtresDecrits = [...Object.values(filtres).filter(Boolean), ...nomsChemin];
  const libellePeriode =
    periode === 'tout'
      ? mois.length
        ? `de ${moisCourt(mois[0])} à ${moisCourt(mois[mois.length - 1])}`
        : 'Toute la période'
      : periode.startsWith('A:')
        ? periode.slice(2)
        : libelleMois(periode.slice(2));

  const choisirSource = (cle: string) => {
    const s = SOURCES.find((x) => x.cle === cle) ?? SOURCES[0];
    setCleSource(s.cle);
    setIndicateurs([s.indicateurs[0].cle]);
    setFiltres({});
    setChemin([]);
    setPar(s.indicateurs[0].territoire ? 'sous' : 'mois');
    setMode('n');
  };

  const basculer = (cle: string) => {
    if (indicateurs.includes(cle)) {
      if (indicateurs.length > 1) setIndicateurs(indicateurs.filter((x) => x !== cle));
    } else {
      setIndicateurs(
        source.indicateurs.map((i) => i.cle).filter((x) => x === cle || indicateurs.includes(x)),
      );
    }
  };

  const exporter = () => {
    const brut = (v: number, j: number, ligne: number[]) =>
      modeEffectif === 'n'
        ? String(Number.isFinite(v) ? v : 0)
        : cellule(v, j, ligne).replace(/[\u00a0\u202f]/g, ' ');
    telechargerCsv(`exploration-${cleSource}-${parEffectif}.csv`, [
      [libellePar || 'Total', ...choisis.map((i) => i.libelle)],
      ...lignes.map((l) => [l.libelle, ...l.valeurs.map((v, j) => brut(v, j, l.valeurs))]),
      ['Total', ...totaux.map((t, j) => brut(t, j, totaux))],
    ]);
  };

  return (
    <>
      <section className="panneau-m" aria-label="Choix des données">
        <Tabs selectedKey={cleSource} onSelectionChange={(k) => choisirSource(String(k))}>
          <TabList aria-label="Sources" className="xp-onglets">
            {SOURCES.map((s) => (
              <Tab key={s.cle} id={s.cle} className="xp-onglet">
                {s.libelle}
                <span className="xp-onglet__nombre">{s.indicateurs.length}</span>
              </Tab>
            ))}
          </TabList>
          {SOURCES.map((s) => (
            <TabPanel key={s.cle} id={s.cle} className="panneau-m__corps">
              <h2 className="xp-section">Filtres</h2>
              <div className="xp-grille">
                <ChampChoix
                  libelle="Période"
                  valeur={periode}
                  options={[{ id: 'tout', libelle: 'Toute la période' }]}
                  groupes={[
                    { titre: 'Années', options: annees.map((a) => ({ id: `A:${a}`, libelle: a })) },
                    {
                      titre: 'Mois',
                      options: [...mois].reverse().map((m) => ({ id: `M:${m}`, libelle: libelleMois(m) })),
                    },
                  ]}
                  onChange={setPeriode}
                />
                {dimensionsSource.map((d) => {
                  const applicable = choisis.some((i) => i.dimensions.includes(d));
                  const dim = DIMENSIONS[d];
                  return (
                    <ChampChoix
                      key={d}
                      libelle={dim.libelle}
                      valeur={filtres[d] ?? ''}
                      options={[
                        { id: '', libelle: dim.tous },
                        ...dim.valeurs.map((v) => ({ id: v, libelle: v })),
                      ]}
                      desactive={!applicable || dim.valeurs.length === 0}
                      raison={
                        !applicable
                          ? 'Sans objet pour les indicateurs choisis'
                          : 'Valeurs pas encore disponibles'
                      }
                      onChange={(v) => setFiltres((f) => ({ ...f, [d]: v || undefined }))}
                    />
                  );
                })}
              </div>
              {s.indicateurs.some((i) => i.territoire) && (
                <div className="xp-grille xp-grille--territoire">
                  {NIVEAUX_TERRITOIRE.map((n, k) => {
                    // Un niveau s'ouvre dès que le niveau au-dessus est choisi (la région : toujours).
                    const ouvert = k === 0 || !!chemin[k - 1];
                    const options = optionsNiveau(k);
                    return (
                      <ChampChoix
                        key={n.cle}
                        libelle={n.libelle}
                        valeur={chemin[k] ?? ''}
                        options={[
                          { id: '', libelle: ouvert ? TOUTES_ZONES[k] : VIDE_TERRITOIRE[k] },
                          ...(ouvert ? options : []),
                        ]}
                        desactive={!territoireOk || !ouvert || (k > 0 && options.length === 0)}
                        raison={
                          !territoireOk
                            ? 'Un des indicateurs choisis ne se ventile pas par territoire'
                            : !ouvert
                              ? `${VIDE_TERRITOIRE[k]} d’abord`
                              : 'Aucune zone de ce niveau dans la zone choisie'
                        }
                        onChange={(v) => choisirNiveau(k, v)}
                      />
                    );
                  })}
                </div>
              )}
              <div className="xp-filet" />
              <div className="xp-bas">
                <div className="xp-champ">
                  <span id={`xp-ind-${s.cle}`} className="champ-choix__libelle">
                    Indicateurs
                  </span>
                  <details className="xp-indicateurs">
                    <summary aria-labelledby={`xp-ind-${s.cle}`}>
                      <span>
                        {choisis[0]?.libelle}
                        {choisis.length > 1 ? ` + ${choisis.length - 1}` : ''}
                      </span>
                      <Chevron bas taille={12} />
                    </summary>
                    <div className="xp-indicateurs__liste" role="group" aria-label="Indicateurs">
                      {s.indicateurs.map((i) => (
                        <label key={i.cle}>
                          <input
                            type="checkbox"
                            checked={indicateurs.includes(i.cle)}
                            onChange={() => basculer(i.cle)}
                          />
                          {i.libelle}
                        </label>
                      ))}
                    </div>
                  </details>
                </div>
                <ChampChoix
                  libelle="Afficher par"
                  valeur={parEffectif}
                  options={optionsPar}
                  onChange={setPar}
                />
                <ChampChoix
                  libelle="Valeurs"
                  valeur={modeEffectif}
                  options={[
                    { id: 'n', libelle: 'Nombres' },
                    { id: 'pt', libelle: 'Part du total (%)' },
                    ...(choisis.length > 1
                      ? [{ id: 'pf', libelle: `En % de « ${choisis[0].libelle} »` }]
                      : []),
                  ]}
                  onChange={(v) => setMode(v as Mode)}
                />
                <button type="button" className="xp-csv" onClick={exporter}>
                  <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" className="chevron">
                    <path d="M12 4v11M7 10l5 5 5-5M5 20h14" />
                  </svg>
                  Exporter en CSV
                </button>
              </div>
              {s.note && <p className="xp-note">{s.note}</p>}
              {choisis.some((i) => i.cle === 'pre') && chemin.length >= 2 && (
                <p className="xp-note">
                  Les pré-inscriptions ne sont situées qu’à la préfecture de résidence déclarée : le total de
                  la zone est exact, le détail plus fin est à 0.
                </p>
              )}
              {!territoireOk && s.indicateurs.some((i) => i.territoire) && (
                <p className="xp-note">
                  Un des indicateurs choisis ne se ventile pas par territoire : les filtres géographiques sont
                  ignorés.
                </p>
              )}
            </TabPanel>
          ))}
        </Tabs>
      </section>

      <Panneau
        id="titre-resultat"
        titre={titreResultat}
        sousTitre={`${source.libelle} · ${libellePeriode} · ${filtresDecrits.length ? filtresDecrits.join(' · ') : 'sans filtre'}.`}
        surTitre={
          chemin.length ? (
            <span className="fil-ariane">
              <button type="button" className="fil-ariane__lien" onClick={() => setChemin([])}>
                Togo
              </button>
              {nomsChemin.map((nom, k) => (
                <span key={chemin[k]} className="fil-ariane__etape">
                  <Chevron taille={11} />
                  {k < chemin.length - 1 ? (
                    <button
                      type="button"
                      className="fil-ariane__lien"
                      onClick={() => setChemin(chemin.slice(0, k + 1))}
                    >
                      {nom}
                    </button>
                  ) : (
                    <span aria-current="location">{nom}</span>
                  )}
                </span>
              ))}
            </span>
          ) : undefined
        }
      >
        <GrandChiffre valeur={nf(totaux[0])} unite={`${choisis[0]?.libelle.toLowerCase()} au total`} />
        {parEffectif !== 'total' && (
          <div
            className="tableau-m-defile xp-tableau"
            tabIndex={0}
            role="group"
            aria-label="Tableau, défilable horizontalement"
          >
            <table className="tableau-m">
              <caption className="visuellement-cache">{titreResultat}</caption>
              <thead>
                <tr>
                  <th scope="col">{libellePar}</th>
                  {choisis.map((i) => (
                    <th key={i.cle} scope="col">
                      {i.libelle}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tranche.lignes.map((l) => (
                  <tr key={l.id}>
                    <th scope="row">
                      {l.ouvrable && territoireOk ? (
                        <button
                          type="button"
                          className="bouton-zone"
                          onClick={() => {
                            setChemin([...chemin, l.id]);
                            setPar('sous');
                          }}
                        >
                          {l.libelle}
                          <Chevron />
                        </button>
                      ) : (
                        l.libelle
                      )}
                    </th>
                    {l.valeurs.map((v, j) => (
                      <td key={j}>{cellule(v, j, l.valeurs)}</td>
                    ))}
                  </tr>
                ))}
                <tr className="total">
                  <th scope="row">Total</th>
                  {totaux.map((t, j) => (
                    <td key={j}>
                      {modeEffectif === 'pt' && Number.isFinite(t) ? pct(1) : cellule(t, j, totaux)}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        )}
        {parEffectif !== 'total' && (
          <Pagination
            page={tranche.page}
            pages={tranche.pages}
            debut={tranche.debut}
            fin={tranche.fin}
            total={tranche.total}
            taille={taille}
            quoi="lignes"
            onPage={allerPage}
            onTaille={(t) => {
              setTaille(t);
              allerPage(0);
            }}
          />
        )}
      </Panneau>
    </>
  );
}
