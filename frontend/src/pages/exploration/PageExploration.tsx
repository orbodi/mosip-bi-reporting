import { useState } from 'react';
import { Tab, TabList, TabPanel, Tabs } from 'react-aria-components';
import type { LigneZone } from '../../api/client';
import { useTerritoire } from '../../api/enrolement';
import { useMeta } from '../../api/meta';
import { ChampChoix, type OptionChoix } from '../../composants/blocs/ChampChoix';
import { Chevron } from '../../composants/blocs/Icone';
import { GrandChiffre } from '../../composants/blocs/Indicateur';
import { Panneau } from '../../composants/blocs/Panneau';
import { CONTOURS_PREFECTURES } from '../../composants/carte/contoursTogo';
import { Bandeau } from '../../composants/coque/Bandeau';
import { nf, part, pct } from '../../lib/format';
import { cleNom } from '../../lib/territoire';
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

/** Colonnes de l'API Territoire correspondant aux indicateurs d'enrôlement. */
const CHAMP_ENROLEMENT: Record<
  string,
  keyof Pick<LigneZone, 'inscriptions' | 'niuGeneres' | 'enCours' | 'echouees' | 'rejetees'>
> = {
  ins: 'inscriptions',
  niu: 'niuGeneres',
  enc: 'enCours',
  ech: 'echouees',
  rej: 'rejetees',
};

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
 * Exploration des données (maquette/pages/Technique.dc.html) : 24 indicateurs de 5 sources, filtres, ventilation et
 * export CSV. Seule la source Enrôlement a une API (par région ou par préfecture, sans filtre de profil) ; ailleurs
 * le tableau garde sa forme, chiffres « – ».
 */
export function PageExploration({ page }: { page: DefinitionPage }) {
  return (
    <>
      <Bandeau
        titre={page.titre}
        source={page.source}
        sansPeriode
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
  const [regionChoisie, setRegionChoisie] = useState<string>('');
  const [par, setPar] = useState<string>('region');
  const [mode, setMode] = useState<Mode>('n');

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

  const optionsPar: OptionChoix[] = [
    ...(territoireOk && !regionChoisie ? [{ id: 'region', libelle: 'Région' }] : []),
    ...(territoireOk ? [{ id: 'pref', libelle: 'Préfecture' }] : []),
    ...(!periode.startsWith('A:') && !periode.startsWith('M:') ? [{ id: 'annee', libelle: 'Année' }] : []),
    ...(!periode.startsWith('M:') ? [{ id: 'mois', libelle: 'Mois' }] : []),
    ...dimensionsCommunes
      .filter((d) => !filtres[d] && DIMENSIONS[d].valeurs.length)
      .map((d) => ({ id: d, libelle: DIMENSIONS[d].libelle })),
    { id: 'total', libelle: 'Total seul' },
  ];
  const parEffectif = optionsPar.some((o) => o.id === par) ? par : optionsPar[0].id;
  const modeEffectif: Mode = mode === 'pf' && choisis.length < 2 ? 'n' : mode;

  const nomRegion = regions.find((r) => r.code === regionChoisie)?.nom;
  const plage = plageDe(periode);
  // Données réelles : Enrôlement, sans filtre de profil ni de type, par région, par préfecture d'une région, ou total.
  const reel =
    cleSource === 'enrol' &&
    Object.values(filtres).every((v) => !v) &&
    (parEffectif === 'region' || parEffectif === 'total' || (parEffectif === 'pref' && !!regionChoisie));
  const territoire = useTerritoire(plage, regionChoisie || undefined, reel);
  const lignesApi = reel ? territoire.data?.lignes.filter((l) => !l.horsReferentiel) : undefined;

  const valeursDe = (
    l?: Pick<LigneZone, 'inscriptions' | 'niuGeneres' | 'enCours' | 'echouees' | 'rejetees'>,
  ) => choisis.map((i) => (l && CHAMP_ENROLEMENT[i.cle] ? l[CHAMP_ENROLEMENT[i.cle]] : Number.NaN));

  const lignes = ((): { id: string; libelle: string; valeurs: number[]; ouvrable?: boolean }[] => {
    if (parEffectif === 'total') return [];
    if (lignesApi && (parEffectif === 'region' || parEffectif === 'pref')) {
      return lignesApi.map((l) => ({
        id: l.code,
        libelle: l.nom,
        valeurs: valeursDe(l),
        ouvrable: parEffectif === 'region',
      }));
    }
    const inconnues = () => choisis.map(() => Number.NaN);
    if (parEffectif === 'region') {
      return regions.map((r) => ({ id: r.code, libelle: r.nom, valeurs: inconnues(), ouvrable: true }));
    }
    if (parEffectif === 'pref') {
      return CONTOURS_PREFECTURES.filter(
        (p) => !nomRegion || cleNom(p.region ?? '') === cleNom(nomRegion),
      ).map((p) => ({
        id: p.nom,
        libelle: p.nom,
        valeurs: inconnues(),
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

  const cellule = (v: number, j: number, ligne: number[]) => {
    if (!Number.isFinite(v)) return '–';
    if (modeEffectif === 'pt') return pct(part(v, totaux[j]));
    if (modeEffectif === 'pf' && j > 0) return pct(part(v, ligne[0]));
    return nf(v);
  };

  const libellePar = optionsPar.find((o) => o.id === parEffectif)?.libelle ?? '';
  const titreResultat = `${choisis.map((i) => i.libelle).join(', ')}${parEffectif !== 'total' ? ` par ${libellePar.toLowerCase()}` : ''}`;
  const filtresDecrits = [...Object.values(filtres).filter(Boolean), ...(nomRegion ? [nomRegion] : [])];
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
    setRegionChoisie('');
    setPar(s.indicateurs[0].territoire ? 'region' : 'mois');
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
      !Number.isFinite(v)
        ? ''
        : modeEffectif === 'n'
          ? String(v)
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
                  {NIVEAUX_TERRITOIRE.map((n, i) =>
                    i === 0 ? (
                      <ChampChoix
                        key={n.cle}
                        libelle={n.libelle}
                        valeur={regionChoisie}
                        options={[
                          { id: '', libelle: 'Toutes' },
                          ...regions.map((r) => ({ id: r.code, libelle: r.nom })),
                        ]}
                        desactive={!territoireOk}
                        raison="Un des indicateurs choisis ne se ventile pas par territoire"
                        onChange={(v) => {
                          setRegionChoisie(v);
                          if (v && parEffectif === 'region') setPar('pref');
                        }}
                      />
                    ) : (
                      <ChampChoix
                        key={n.cle}
                        libelle={n.libelle}
                        valeur=""
                        options={[{ id: '', libelle: VIDE_TERRITOIRE[i] }]}
                        desactive
                        raison="Référentiel des communes, cantons, localités et centres pas encore chargé"
                        onChange={() => {}}
                      />
                    ),
                  )}
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
          nomRegion ? (
            <span className="fil-ariane">
              <button
                type="button"
                className="fil-ariane__lien"
                onClick={() => {
                  setRegionChoisie('');
                  setPar('region');
                }}
              >
                Togo
              </button>
              <Chevron taille={11} />
              <span aria-current="location">{nomRegion}</span>
            </span>
          ) : undefined
        }
      >
        {!reel && (
          <p className="note-source xp-resultat__note" role="note">
            {cleSource === 'enrol'
              ? 'Ventilation pas encore disponible : seules les ventilations par région et par préfecture, sans filtre de profil ni de type, ont une API.'
              : `Source « ${source.libelle} » pas encore raccordée au BI : le tableau garde sa forme, chiffres « – ».`}
          </p>
        )}
        {reel && territoire.isError && (
          <p role="alert" className="alerte-donnees alerte-donnees--haut">
            Chiffres indisponibles pour le moment. Ils réapparaîtront dès que l’API répondra.
          </p>
        )}
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
                {lignes.map((l) => (
                  <tr key={l.id}>
                    <th scope="row">
                      {l.ouvrable && territoireOk ? (
                        <button
                          type="button"
                          className="bouton-zone"
                          onClick={() => {
                            setRegionChoisie(l.id);
                            setPar('pref');
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
      </Panneau>
    </>
  );
}
