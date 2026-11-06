import { useNavigate, useSearch } from '@tanstack/react-router';
import { useEffect, useState } from 'react';
import { Tab, TabList, TabPanel, Tabs } from 'react-aria-components';
import type { LigneZone, Territoire } from '../../api/client';
import { useExplorationAuthentifications, type ParametresExploration } from '../../api/authentifications';
import { useExplorationCartes, type ParCartes } from '../../api/cartes';
import { useTerritoire } from '../../api/enrolement';
import { useMeta } from '../../api/meta';
import { ChampChoix, type OptionChoix } from '../../composants/blocs/ChampChoix';
import { Chevron } from '../../composants/blocs/Icone';
import { GrandChiffre } from '../../composants/blocs/Indicateur';
import { Pagination } from '../../composants/blocs/Pagination';
import { Panneau } from '../../composants/blocs/Panneau';
import { Bandeau } from '../../composants/coque/Bandeau';
import { TYPES_AUTHENTIFICATION } from '../../lib/authentifications';
import {
  basculerIndicateur,
  changerSource,
  ecrireRecherche,
  lireEtat,
  reinitialiser,
  trierLignes,
  trierPar,
  type EtatExploration,
  type Mode,
} from '../../lib/etatExploration';
import type { FiltresUrl } from '../../lib/filtresUrl';
import { nf, part, pct } from '../../lib/format';
import { paginer, type TaillePage } from '../../lib/pagination';
import {
  PERSONNALISEE,
  RACCOURCIS,
  datesPersonnalisees,
  erreurPersonnalisee,
  estPersonnalisee,
  estRaccourci,
  libellePersonnalisee,
  libelleRaccourci,
  periodePersonnalisee,
  plageExploration,
} from '../../lib/periodeExploration';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import type { DefinitionPage } from '../pages';
import {
  DIMENSIONS,
  NIVEAUX_TERRITOIRE,
  NOMBRE_INDICATEURS,
  RAISON_INDISPONIBLE,
  SOURCES,
  type CleDimension,
} from './catalogue';
import './exploration.css';

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

/** Authentifications (05/11/2026) : colonnes de l'API Exploration et ventilations correspondantes. */
const CHAMP_AUTH: Record<string, 'requetes' | 'reussies' | 'echouees'> = {
  req: 'requetes',
  ok: 'reussies',
  ko: 'echouees',
};
const PAR_AUTH: Record<string, ParametresExploration['par']> = {
  annee: 'annee',
  mois: 'mois',
  taut: 'type',
  cause: 'motif',
  part: 'appelant',
};
/** Impression des cartes (05/11/2026) : colonnes de l'API Exploration ; ventilations sous-zone, année, mois, total. */
const CHAMP_CARTES: Record<string, 'demandes' | 'expediees' | 'remises' | 'aRemettre'> = {
  dem: 'demandes',
  exp: 'expediees',
  rem: 'remises',
  arem: 'aRemettre',
};
const PAR_CARTES: Partial<Record<string, ParCartes>> = { sous: 'sous', annee: 'annee', mois: 'mois' };
const PERIMETRES_AUTH: OptionChoix[] = [
  { id: 'usagers', libelle: 'Usagers' },
  { id: 'paquets', libelle: 'Traitement des paquets' },
];
const libelleType = (code: string) => TYPES_AUTHENTIFICATION.find((t) => t.code === code)?.libelle ?? code;
// Le catalogue des motifs du pipeline écrit l'apostrophe droite.
const apostrophe = (texte: string) => texte.replace(/'/g, '’');

/** Libellé en minuscule dans une phrase, sauf un sigle (« inscriptions », mais « NIU générés »). */
const minuscule = (t: string) => (/^[A-Z]{2}/.test(t) ? t : t.charAt(0).toLowerCase() + t.slice(1));

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
 * Exploration des données (maquette/pages/Technique.dc.html ; lots A et B du 05/11/2026, maquette
 * maquette-exploration-AB) : indicateurs de 5 sources, filtres, ventilation, tri et export CSV. Enrôlement (par
 * territoire), Impression des cartes et Authentifications lisent l'API ; un filtre ou une ventilation sans données est
 * grisé, avec sa raison. ABIS et IDPS gardent leur forme, indicateurs à 0 (décision du 20/10/2026). Tous les choix
 * sont dans l'adresse (lib/etatExploration).
 */
export function PageExploration({ page }: { page: DefinitionPage }) {
  return (
    <>
      <Bandeau
        titre={page.titre}
        source={page.source}
        chapeau={`Les ${NOMBRE_INDICATEURS} indicateurs des cinq sources du BI : choisissez une source et les indicateurs, filtrez, puis choisissez ce qui s’affiche en lignes.`}
      />
      <div className="contenu page-m">
        <Explorateur />
      </div>
    </>
  );
}

/**
 * Champs Du et Au de la période personnalisée : saisie gardée ici (taper l'année passe par 0002, 0020…, l'adresse
 * suit un instant plus tard), reportée dans l'adresse à chaque changement.
 */
function SaisieDates({
  periode,
  bornes,
  invalide,
  idErreur,
  onChange,
}: {
  periode: string;
  bornes?: { du: string; au: string };
  invalide: boolean;
  idErreur?: string;
  onChange: (periode: string) => void;
}) {
  const [dates, setDates] = useState(() => datesPersonnalisees(periode));
  const saisir = (du: string, au: string) => {
    setDates({ du, au });
    onChange(periodePersonnalisee(du, au));
  };
  return (
    <>
      <label className="xp-champ">
        <span className="champ-choix__libelle">Du</span>
        <input
          type="date"
          className="xp-date"
          value={dates.du}
          min={bornes?.du}
          max={bornes?.au}
          aria-invalid={invalide && !!dates.du}
          aria-describedby={idErreur}
          onChange={(e) => saisir(e.target.value, dates.au)}
        />
      </label>
      <label className="xp-champ">
        <span className="champ-choix__libelle">Au</span>
        <input
          type="date"
          className="xp-date"
          value={dates.au}
          min={dates.du || bornes?.du}
          max={bornes?.au}
          aria-invalid={invalide && !!dates.au}
          aria-describedby={idErreur}
          onChange={(e) => saisir(dates.du, e.target.value)}
        />
      </label>
    </>
  );
}

function Explorateur() {
  const recherche: FiltresUrl = useSearch({ strict: false });
  const naviguer = useNavigate();
  const etat = lireEtat(recherche);
  // Champs de la période personnalisée : recréés quand la période change autrement que par leur saisie.
  const [cleDates, setCleDates] = useState(0);
  // Chaque choix réécrit l'adresse (sans nouvelle entrée d'historique : Retour quitte l'Exploration telle quelle).
  const changer = (suivant: EtatExploration, depuisDates = false) => {
    if (!depuisDates && suivant.periode !== etat.periode) setCleDates((c) => c + 1);
    naviguer({
      to: '.',
      search: (precedent: FiltresUrl) => ({ ...precedent, ...ecrireRecherche(suivant) }),
      replace: true,
      resetScroll: false,
    });
  };

  const { source: cleSource, indicateurs, periode, filtres, perimetre: perimetreAuth, chemin, mode } = etat;
  const source = SOURCES.find((s) => s.cle === cleSource) ?? SOURCES[0];
  // Pagination du tableau (beaucoup de cantons, de localités ou de mois) ; l'export CSV garde toutes les lignes.
  const [taille, setTaille] = useState<TaillePage>(20);
  const [page, setPage] = useState(0);
  const [lienCopie, setLienCopie] = useState(false);
  useEffect(() => {
    if (!lienCopie) return;
    const minuteur = setTimeout(() => setLienCopie(false), 2500);
    return () => clearTimeout(minuteur);
  }, [lienCopie]);

  const { regions } = useFiltreRegion();
  const meta = useMeta();
  const fraicheur = meta.data?.sources.find((s) => s.source === source.fraicheur);

  const choisis = source.indicateurs.filter((i) => indicateurs.includes(i.cle));
  const territoireOk = choisis.every((i) => i.territoire);
  const dimensionsSource = (Object.keys(DIMENSIONS) as CleDimension[]).filter((d) =>
    source.indicateurs.some((i) => i.dimensions.includes(d)),
  );
  const dimensionsCommunes = dimensionsSource.filter((d) => choisis.every((i) => i.dimensions.includes(d)));
  // Sans données dans l'Exploration (grisés, 05/11/2026) : profil et type de l'Enrôlement, mois et années.
  const dimensionIndisponible = (d: CleDimension) => !!source.indisponibles?.dimensions.includes(d);
  const ventilationIndisponible = (v: string) => !!source.indisponibles?.ventilations.includes(v);

  const mois =
    fraicheur?.premiereDonnee && fraicheur.derniereDonnee
      ? moisEntre(fraicheur.premiereDonnee.slice(0, 7), fraicheur.derniereDonnee.slice(0, 7))
      : [];
  const annees = [...new Set(mois.map((m) => m.slice(0, 4)))];
  // Période personnalisée et raccourcis (05/11/2026) : dates bornées aux données de la source.
  const bornes =
    fraicheur?.premiereDonnee && fraicheur.derniereDonnee
      ? { du: fraicheur.premiereDonnee.slice(0, 10), au: fraicheur.derniereDonnee.slice(0, 10) }
      : undefined;
  const perso = estPersonnalisee(periode);
  const raccourci = estRaccourci(periode);
  const datesPerso = datesPersonnalisees(periode);
  const erreurPerso = perso ? erreurPersonnalisee(periode, bornes) : undefined;
  const plage = plageExploration(periode, bornes);
  // Pas d'appel tant qu'une période n'est pas utilisable : personnalisée invalide, raccourci sans bornes connues.
  const periodePrete = !erreurPerso && (!raccourci || !!plage);
  // Mois et années de la période choisie (lignes des ventilations « Mois » et « Année »).
  const moisPeriode = plage ? mois.filter((m) => m >= plage.du.slice(0, 7) && m <= plage.au.slice(0, 7)) : mois;
  const anneesPeriode = [...new Set(moisPeriode.map((m) => m.slice(0, 4)))];

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
  const choisirChemin = (suivant: string[]) => changer({ ...etat, chemin: suivant });
  const choisirNiveau = (k: number, code: string) =>
    choisirChemin(code ? [...chemin.slice(0, k), code] : chemin.slice(0, k));

  // Valeurs des filtres de l'onglet Authentifications, lues dans les données (toute la durée du périmètre).
  const auth = cleSource === 'auth';
  const valeursAuth = useExplorationAuthentifications(undefined, { perimetre: perimetreAuth, par: 'total' }, auth)
    .data?.valeurs;
  const optionsDimension = (d: CleDimension): OptionChoix[] => {
    if (auth && d === 'taut') {
      const codes = valeursAuth?.types ?? TYPES_AUTHENTIFICATION.map((x) => x.code).filter((c) => c !== 'non_classe');
      return codes.map((c) => ({ id: c, libelle: libelleType(c) }));
    }
    if (auth && d === 'cause') {
      return (valeursAuth?.motifs ?? []).map((m) => ({ id: m.code, libelle: apostrophe(m.libelle) }));
    }
    if (auth && d === 'part') return (valeursAuth?.appelants ?? []).map((a) => ({ id: a, libelle: a }));
    return DIMENSIONS[d].valeurs.map((v) => ({ id: v, libelle: v }));
  };
  const libelleFiltre = (d: CleDimension, v: string) => optionsDimension(d).find((o) => o.id === v)?.libelle ?? v;
  // Raison d'un filtre sans objet : l'indicateur qui l'ouvrirait, s'il n'y en a qu'un (« Requêtes échouées »).
  const raisonSansObjet = (d: CleDimension) => {
    const porteurs = source.indicateurs.filter((i) => i.dimensions.includes(d));
    return porteurs.length === 1
      ? `Choisissez l’indicateur « ${porteurs[0].libelle} »`
      : 'Sans objet pour les indicateurs choisis';
  };

  const indisponible = (id: string, libelle: string): OptionChoix =>
    ventilationIndisponible(id)
      ? { id, libelle, desactive: true, raison: RAISON_INDISPONIBLE }
      : { id, libelle };
  const optionsPar: OptionChoix[] = [
    ...(territoireOk && niveauSuivant ? [{ id: 'sous', libelle: niveauSuivant.libelle }] : []),
    ...(!periode.startsWith('A:') && !periode.startsWith('M:') && (!perso || anneesPeriode.length > 1)
      ? [indisponible('annee', 'Année')]
      : []),
    ...(!periode.startsWith('M:') ? [indisponible('mois', 'Mois')] : []),
    ...dimensionsCommunes
      .filter((d) => !filtres[d] && optionsDimension(d).length)
      .map((d) => indisponible(d, DIMENSIONS[d].libelle)),
    { id: 'total', libelle: 'Total seul' },
  ];
  const optionsParOuvertes = optionsPar.filter((o) => !o.desactive);
  const par = etat.par ?? (source.indicateurs[0].territoire ? 'sous' : 'mois');
  const parEffectif = optionsParOuvertes.some((o) => o.id === par) ? par : optionsParOuvertes[0].id;
  const modeEffectif: Mode = mode === 'pf' && choisis.length < 2 ? 'n' : mode;

  const nomsChemin = chemin.map((_, k) => nomDe(k));
  // Données réelles de l'Enrôlement : par sous-zone de la zone choisie, ou total.
  const reel = cleSource === 'enrol' && periodePrete && (parEffectif === 'sous' || parEffectif === 'total');
  const territoire = useTerritoire(plage, zoneChoisie, reel);
  const lignesApi = reel ? territoire.data?.lignes.filter((l) => !l.horsReferentiel) : undefined;

  const valeursDe = (l?: Pick<LigneZone, ChampsEnrolement>) =>
    choisis.map((i) => (l && CHAMP_ENROLEMENT[i.cle] ? l[CHAMP_ENROLEMENT[i.cle]] : Number.NaN));
  // On ouvre une sous-zone du niveau attendu qui a elle-même des sous-zones (pas un centre rattaché plus haut).
  const ouvrable = (l: { niveau?: string | null; ouvrable?: boolean }) =>
    !!niveauSuivant &&
    l.niveau === niveauSuivant.cle &&
    !!NIVEAUX_TERRITOIRE[chemin.length + 1] &&
    (l.ouvrable ?? l.niveau !== 'centre');

  // Authentifications : une requête par ventilation et filtres ; jamais sur une période inutilisable.
  const requeteAuth = useExplorationAuthentifications(
    plage,
    {
      perimetre: perimetreAuth,
      type: filtres.taut,
      motif: filtres.cause,
      appelant: filtres.part,
      par: PAR_AUTH[parEffectif] ?? 'total',
    },
    auth && periodePrete,
  );
  const exploAuth = requeteAuth.data;
  // Impression des cartes : une requête par zone, période et ventilation ; on n'affiche que la réponse à la
  // ventilation et à la zone en cours (pas les lignes de la précédente pendant le chargement).
  const cartes = cleSource === 'cartes';
  const parCartes = PAR_CARTES[parEffectif] ?? 'total';
  const requeteCartes = useExplorationCartes(plage, zoneChoisie, parCartes, cartes && periodePrete);
  const reponseCartes = requeteCartes.data;
  const exploCartes =
    cartes && reponseCartes?.par === parCartes && (reponseCartes.zone ?? undefined) === zoneChoisie
      ? reponseCartes
      : undefined;
  // Chargement visible (05/11/2026) : les chiffres précédents restent affichés, en pâle, jusqu'à la réponse.
  const enCours =
    (reel && territoire.isFetching) ||
    (auth && periodePrete && requeteAuth.isFetching) ||
    (cartes && periodePrete && requeteCartes.isFetching);
  const libelleLigneAuth = (cle: string, libelle: string) =>
    parEffectif === 'mois'
      ? libelleMois(cle)
      : parEffectif === 'taut'
        ? libelleType(cle)
        : apostrophe(libelle);

  const lignes = ((): { id: string; libelle: string; valeurs: number[]; ouvrable?: boolean }[] => {
    if (parEffectif === 'total') return [];
    if (auth && exploAuth) {
      return exploAuth.lignes.map((l) => ({
        id: l.cle,
        libelle: libelleLigneAuth(l.cle, l.libelle),
        valeurs: choisis.map((i) => l.chiffres[CHAMP_AUTH[i.cle]] ?? Number.NaN),
      }));
    }
    if (exploCartes) {
      return exploCartes.lignes.map((l) => ({
        id: l.cle,
        libelle: parEffectif === 'mois' ? libelleMois(l.cle) : l.libelle,
        valeurs: choisis.map((i) => l.chiffres[CHAMP_CARTES[i.cle]] ?? Number.NaN),
        ouvrable: parEffectif === 'sous' && ouvrable(l),
      }));
    }
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
    if (parEffectif === 'annee') return anneesPeriode.map((a) => ({ id: a, libelle: a, valeurs: inconnues() }));
    if (parEffectif === 'mois') {
      return moisPeriode.map((m) => ({ id: m, libelle: libelleMois(m), valeurs: inconnues() }));
    }
    const dim = DIMENSIONS[parEffectif as CleDimension];
    return dim ? dim.valeurs.map((v) => ({ id: v, libelle: v, valeurs: inconnues() })) : [];
  })();

  const totaux =
    auth && exploAuth
      ? choisis.map((i) => exploAuth.total[CHAMP_AUTH[i.cle]] ?? Number.NaN)
      : exploCartes
        ? choisis.map((i) => exploCartes.total[CHAMP_CARTES[i.cle]] ?? Number.NaN)
        : reel && territoire.data
          ? valeursDe(territoire.data)
          : choisis.map(() => Number.NaN);
  // Tri au clic sur un titre de colonne (05/11/2026), avant la pagination.
  const lignesTriees = trierLignes(
    lignes,
    etat.tri,
    choisis.map((i) => i.cle),
  );
  // La page revient à 1 quand les lignes changent (autre zone, ventilation, période ou tri).
  const cleLignes = `${cleSource}|${parEffectif}|${chemin.join('/')}|${periode}|${perimetreAuth}|${etat.tri?.colonne}:${etat.tri?.sens}`;
  const [clePage, setClePage] = useState(cleLignes);
  const tranche = paginer(lignesTriees, clePage === cleLignes ? page : 0, taille);
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
  const filtresDecrits = [
    ...(auth ? [PERIMETRES_AUTH.find((o) => o.id === perimetreAuth)?.libelle ?? ''] : []),
    ...(Object.entries(filtres) as [CleDimension, string | undefined][])
      .filter(([, v]) => !!v)
      .map(([d, v]) => libelleFiltre(d, v as string)),
    ...nomsChemin,
  ];
  const libellePeriode =
    periode === 'tout'
      ? mois.length
        ? `de ${moisCourt(mois[0])} à ${moisCourt(mois[mois.length - 1])}`
        : 'Toute la période'
      : perso
        ? libellePersonnalisee(periode)
        : raccourci
          ? libelleRaccourci(periode, bornes)
          : periode.startsWith('A:')
            ? periode.slice(2)
            : libelleMois(periode.slice(2));
  // Pastille de la période : le nom court du raccourci, sinon le libellé de la période.
  const pastillePeriode = raccourci
    ? (RACCOURCIS.find((r) => r.id === periode)?.libelle ?? periode)
    : perso
      ? libellePersonnalisee(periode)
      : libellePeriode;

  // Filtres actifs (05/11/2026) : une pastille retirable par choix ; le périmètre des authentifications, sans ✕.
  const actifs: { cle: string; libelle: string; retirer?: () => void }[] = [
    ...(auth ? [{ cle: 'perimetre', libelle: PERIMETRES_AUTH.find((o) => o.id === perimetreAuth)?.libelle ?? '' }] : []),
    ...(periode !== 'tout'
      ? [{ cle: 'periode', libelle: pastillePeriode, retirer: () => changer({ ...etat, periode: 'tout' }) }]
      : []),
    ...(Object.entries(filtres) as [CleDimension, string | undefined][])
      .filter(([, v]) => !!v)
      .map(([d, v]) => ({
        cle: d,
        libelle: `${DIMENSIONS[d].libelle} : ${libelleFiltre(d, v as string)}`,
        retirer: () => changer({ ...etat, filtres: { ...filtres, [d]: undefined } }),
      })),
    ...(chemin.length
      ? [
          {
            cle: 'zone',
            libelle: `${NIVEAUX_TERRITOIRE[chemin.length - 1].libelle} : ${nomsChemin[chemin.length - 1]}`,
            retirer: () => choisirChemin(chemin.slice(0, -1)),
          },
        ]
      : []),
  ];
  const aReinitialiser = actifs.some((a) => a.retirer) || indicateurs.length > 1 || !!etat.par || !!etat.tri;

  const copierLien = () => {
    navigator.clipboard
      ?.writeText(window.location.href)
      .then(() => setLienCopie(true))
      .catch(() => undefined);
  };

  const exporter = () => {
    const brut = (v: number, j: number, ligne: number[]) =>
      modeEffectif === 'n'
        ? String(Number.isFinite(v) ? v : 0)
        : cellule(v, j, ligne).replace(/[  ]/g, ' ');
    telechargerCsv(`exploration-${cleSource}-${parEffectif}.csv`, [
      [libellePar || 'Total', ...choisis.map((i) => i.libelle)],
      ...lignesTriees.map((l) => [l.libelle, ...l.valeurs.map((v, j) => brut(v, j, l.valeurs))]),
      ['Total', ...totaux.map((t, j) => brut(t, j, totaux))],
    ]);
  };

  // Titre de colonne triable : bouton, sens annoncé par aria-sort.
  const enteteTriable = (colonne: string, libelle: string) => {
    const sens = etat.tri?.colonne === colonne ? etat.tri.sens : undefined;
    return (
      <th
        key={colonne}
        scope="col"
        aria-sort={sens === 'asc' ? 'ascending' : sens === 'desc' ? 'descending' : undefined}
      >
        <button type="button" className="xp-tri" onClick={() => changer(trierPar(etat, colonne))}>
          {libelle}
          <span className="xp-tri__sens" aria-hidden="true">
            {sens === 'asc' ? '↑' : sens === 'desc' ? '↓' : '↕'}
          </span>
        </button>
      </th>
    );
  };

  // Niveaux de territoire affichés (05/11/2026) : ceux déjà choisis et le suivant, s'il a des zones.
  const niveauxAffiches = NIVEAUX_TERRITOIRE.map((n, k) => ({ n, k })).filter(
    ({ k }) => k <= chemin.length && (k === 0 || !!chemin[k] || optionsNiveau(k).length > 0),
  );

  return (
    <>
      <section className="panneau-m" aria-label="Choix des données">
        <Tabs
          selectedKey={cleSource}
          // Seulement sur un vrai changement d'onglet : une vue rouverte depuis un lien ne doit pas être remise à zéro.
          onSelectionChange={(k) => String(k) !== cleSource && changer(changerSource(etat, String(k)))}
        >
          <TabList aria-label="Sources" className="xp-onglets">
            {SOURCES.map((s) => (
              <Tab key={s.cle} id={s.cle} className="xp-onglet">
                {s.libelle}
              </Tab>
            ))}
          </TabList>
          {SOURCES.map((s) => (
            <TabPanel key={s.cle} id={s.cle} className="panneau-m__corps">
              <div className="xp-haut">
                {s.cle === 'auth' && (
                  <div className="xp-bloc">
                    <h2 className="xp-section" id={`xp-perimetre-${s.cle}`}>
                      Périmètre
                    </h2>
                    <div className="xp-segment" role="group" aria-labelledby={`xp-perimetre-${s.cle}`}>
                      {PERIMETRES_AUTH.map((o) => (
                        <button
                          key={o.id}
                          type="button"
                          className="xp-segment__bouton"
                          aria-pressed={perimetreAuth === o.id}
                          // Les motifs et les appelants diffèrent d'un périmètre à l'autre.
                          onClick={() =>
                            perimetreAuth !== o.id &&
                            changer({ ...etat, perimetre: o.id as EtatExploration['perimetre'], filtres: {} })
                          }
                        >
                          {o.libelle}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                <div className="xp-bloc">
                  <h2 className="xp-section" id={`xp-ind-${s.cle}`}>
                    Indicateurs <span className="xp-section__aide">(un ou plusieurs)</span>
                  </h2>
                  <div className="xp-puces" role="group" aria-labelledby={`xp-ind-${s.cle}`}>
                    {s.indicateurs.map((i) => (
                      <button
                        key={i.cle}
                        type="button"
                        className="xp-puce"
                        aria-pressed={indicateurs.includes(i.cle)}
                        onClick={() => changer(basculerIndicateur(etat, i.cle))}
                      >
                        {i.libelle}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              <div className="xp-filet" />
              <h2 className="xp-section">Période et filtres</h2>
              <div className="xp-grille">
                <ChampChoix
                  libelle="Période"
                  valeur={perso ? PERSONNALISEE : periode}
                  options={[]}
                  groupes={[
                    { titre: 'Raccourcis', options: RACCOURCIS.map((r) => ({ id: r.id, libelle: r.libelle })) },
                    {
                      titre: 'Autres',
                      options: [
                        { id: 'tout', libelle: 'Toute la période' },
                        { id: PERSONNALISEE, libelle: 'Personnalisée' },
                      ],
                    },
                    { titre: 'Années', options: annees.map((a) => ({ id: `A:${a}`, libelle: a })) },
                    {
                      titre: 'Mois',
                      options: [...mois].reverse().map((m) => ({ id: `M:${m}`, libelle: libelleMois(m) })),
                    },
                  ]}
                  onChange={(v) =>
                    changer({
                      ...etat,
                      periode: v === PERSONNALISEE ? (perso ? periode : periodePersonnalisee('', '')) : v,
                    })
                  }
                />
                {perso && (
                  <>
                    <SaisieDates
                      key={cleDates}
                      periode={periode}
                      bornes={bornes}
                      invalide={!!erreurPerso}
                      idErreur={erreurPerso && datesPerso.du ? `xp-erreur-${s.cle}` : undefined}
                      onChange={(v) => changer({ ...etat, periode: v }, true)}
                    />
                    {!datesPerso.du ? (
                      <p className="xp-aide">Choisissez la date de début ; laissez « Au » vide pour un seul jour.</p>
                    ) : (
                      erreurPerso && (
                        <p id={`xp-erreur-${s.cle}`} className="xp-erreur" role="alert">
                          {erreurPerso}
                        </p>
                      )
                    )}
                  </>
                )}
                {dimensionsSource.map((d) => {
                  const applicable = choisis.some((i) => i.dimensions.includes(d));
                  const dim = DIMENSIONS[d];
                  const options = optionsDimension(d);
                  const sansDonnees = dimensionIndisponible(d);
                  return (
                    <ChampChoix
                      key={d}
                      libelle={dim.libelle}
                      valeur={filtres[d] ?? ''}
                      options={[{ id: '', libelle: dim.tous }, ...options]}
                      desactive={sansDonnees || !applicable || options.length === 0}
                      raison={
                        sansDonnees
                          ? RAISON_INDISPONIBLE
                          : !applicable
                            ? raisonSansObjet(d)
                            : 'Valeurs pas encore disponibles'
                      }
                      onChange={(v) => changer({ ...etat, filtres: { ...filtres, [d]: v || undefined } })}
                    />
                  );
                })}
              </div>
              {s.indicateurs.some((i) => i.territoire) && (
                <div className="xp-grille xp-grille--territoire">
                  {niveauxAffiches.map(({ n, k }) => (
                    <ChampChoix
                      key={n.cle}
                      libelle={n.libelle}
                      valeur={chemin[k] ?? ''}
                      options={[{ id: '', libelle: TOUTES_ZONES[k] }, ...optionsNiveau(k)]}
                      desactive={!territoireOk}
                      raison="Un des indicateurs choisis ne se ventile pas par territoire"
                      onChange={(v) => choisirNiveau(k, v)}
                    />
                  ))}
                </div>
              )}
              <div className="xp-filet" />
              <div className="xp-bas">
                <ChampChoix
                  libelle="Afficher par"
                  valeur={parEffectif}
                  options={optionsPar}
                  onChange={(v) => changer({ ...etat, par: v })}
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
                  onChange={(v) => changer({ ...etat, mode: v as Mode })}
                />
                <span className="xp-bas__vide" />
                <button type="button" className="xp-lien" onClick={copierLien}>
                  <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" className="chevron">
                    <path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1" />
                  </svg>
                  {lienCopie ? 'Lien copié' : 'Copier le lien'}
                </button>
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
              {(actifs.length > 0 || aReinitialiser) && (
                <div className="xp-actifs">
                  <span>{actifs.length ? 'Filtres actifs :' : 'Aucun filtre actif.'}</span>
                  <ul className="xp-actifs__liste">
                    {actifs.map((a) => (
                      <li key={a.cle} className="xp-actif">
                        {a.libelle}
                        {a.retirer && (
                          <button
                            type="button"
                            className="xp-actif__retirer"
                            aria-label={`Retirer « ${a.libelle} »`}
                            onClick={a.retirer}
                          >
                            ✕
                          </button>
                        )}
                      </li>
                    ))}
                  </ul>
                  {aReinitialiser && (
                    <button type="button" className="xp-reinitialiser" onClick={() => changer(reinitialiser(etat))}>
                      Réinitialiser
                    </button>
                  )}
                </div>
              )}
            </TabPanel>
          ))}
        </Tabs>
      </section>

      <Panneau
        id="titre-resultat"
        titre={titreResultat}
        sousTitre={`${source.libelle} · ${libellePeriode} · ${filtresDecrits.length ? filtresDecrits.join(' · ') : 'sans filtre'}.`}
        className={enCours ? 'xp-resultat xp-resultat--maj' : 'xp-resultat'}
        aside={
          <p className="xp-chargement" role="status">
            {enCours && (
              <>
                <span className="xp-chargement__roue" aria-hidden="true" />
                Mise à jour des chiffres…
              </>
            )}
          </p>
        }
        surTitre={
          chemin.length ? (
            <span className="fil-ariane">
              <button type="button" className="fil-ariane__lien" onClick={() => choisirChemin([])}>
                Togo
              </button>
              {nomsChemin.map((nom, k) => (
                <span key={chemin[k]} className="fil-ariane__etape">
                  <Chevron taille={11} />
                  {k < chemin.length - 1 ? (
                    <button
                      type="button"
                      className="fil-ariane__lien"
                      onClick={() => choisirChemin(chemin.slice(0, k + 1))}
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
        <div className="xp-chiffres">
          {choisis.map((i, j) => (
            <GrandChiffre
              key={i.cle}
              valeur={nf(totaux[j])}
              unite={j === 0 ? `${minuscule(i.libelle)} au total` : minuscule(i.libelle)}
              detail={
                j > 0 && Number.isFinite(totaux[0]) && totaux[0] > 0
                  ? `${pct(part(totaux[j], totaux[0]))} des ${minuscule(choisis[0].libelle)}`
                  : undefined
              }
            />
          ))}
        </div>
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
                  {enteteTriable('libelle', libellePar)}
                  {choisis.map((i) => enteteTriable(i.cle, i.libelle))}
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
                          onClick={() => changer({ ...etat, chemin: [...chemin, l.id], par: undefined })}
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
