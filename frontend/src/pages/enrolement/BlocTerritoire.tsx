import { useState } from 'react';
import type { LigneZone, Territoire, ZoneParente } from '../../api/client';
import { useTerritoire } from '../../api/enrolement';
import { useRegions } from '../../api/meta';
import { Pagination } from '../../composants/blocs/Pagination';
import { CARTE_REGIONS, carteRegion } from '../../composants/carte/fondsDeCarte';
import { INCONNUE, territoireInconnu } from '../../lib/blocsVides';
import { nf, part, pct } from '../../lib/format';
import { paginer, type TaillePage } from '../../lib/pagination';
import {
  SEUIL_ALERTE_REJET,
  alerteRejet,
  avecPreinscriptions,
  compteZones,
  enTeteNiveau,
  legendeSousZones,
  nomPluriel,
  lignesDuTableau,
  nomNiveau,
  tauxNiu,
  tauxRejet,
  titreTerritoire,
} from '../../lib/territoire';
import { usePlageApi } from '../../lib/usePlagePeriode';
import { useZoneTerritoire } from '../../lib/useZoneTerritoire';
import { CarteTerritoire } from './CarteTerritoire';

function Chevron() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" className="chevron">
      <polyline points="9 6 15 12 9 18" />
    </svg>
  );
}

/** Chiffres de la carte de contexte tant que la région n'est pas chargée (affichés 0). */
const CHIFFRES_INCONNUS = { inscriptions: INCONNUE, niuGeneres: INCONNUE, rejetees: INCONNUE };

/** On descend dans une sous-zone qui a elle-même des sous-zones (jamais dans « Hors référentiel » ni un centre). */
const peutDescendre = (l: LigneZone) => !l.horsReferentiel && (l.ouvrable ?? l.niveau !== 'centre');

/** Ce que l'on trouve en ouvrant une zone de ce niveau (lecteurs d'écran, sous-titre). */
const CONTENU: Record<string, string> = {
  region: 'ses préfectures',
  prefecture: 'ses communes',
  commune: 'ses cantons',
  canton: 'ses localités',
  localite: 'ses centres',
};

/**
 * Carte de contexte : la carte nationale, celle de la région ouverte, ou, plus bas, celle de la région qui contient
 * la zone, avec sa préfecture mise en évidence. Les contours s'arrêtent aux préfectures.
 */
function useCarteDeContexte(
  data: Territoire,
  niveau: string | undefined,
  code: string | undefined,
  plage: ReturnType<typeof usePlageApi>,
) {
  const chemin: ZoneParente[] = [
    ...(data.ascendants ?? []),
    ...(code && niveau ? [{ code, nom: data.perimetre, niveau }] : []),
  ];
  const region = chemin.find((z) => z.niveau === 'region');
  const prefecture = chemin.find((z) => z.niveau === 'prefecture');
  const profonde = !!region && niveau !== 'region';
  const regionData = useTerritoire(plage.plage, region?.code, plage.prete && profonde).data;
  return { region, prefecture, profonde, regionData };
}

/**
 * Bloc « Territoire » (maquette Enrôlement) : vue nationale par région, puis descente niveau par niveau jusqu'aux
 * centres (région → préfecture → commune → canton → localité → centre), fil d'Ariane pour remonter. Carte colorée
 * selon le taux de NIU générés (contours jusqu'aux préfectures), tableau des sous-zones (alerte ▲ au-delà de 3,5 % de
 * rejets). La zone ouverte est dans l'adresse (?zone=…) ; seul ce bloc la suit.
 */
export function BlocTerritoire() {
  const plageApi = usePlageApi('enrolement');
  const { plage, prete } = plageApi;
  const { code, choisir } = useZoneTerritoire();
  const { data: regions = [] } = useRegions();
  const requete = useTerritoire(plage, code, prete);
  const { isPending } = requete;
  // Total national pour situer une zone (« 31,1 % du total national »).
  const national = useTerritoire(plage, undefined, prete && !!code);

  // Sans réponse de l'API : les zones attendues (régions du filtre, ou contours de la carte), chiffres à 0.
  const vide = !requete.data;
  const regionConnue = code ? regions.find((r) => r.code === code) : undefined;
  const nomAttendu = code ? (regionConnue?.nom ?? code) : undefined;
  const zonesAttendues = !code
    ? regions.length > 1
      ? regions
      : CARTE_REGIONS.contours.map((c) => ({ code: c.nom, nom: c.nom }))
    : regionConnue
      ? (carteRegion(regionConnue.nom)?.contours ?? []).map((c) => ({ code: c.nom, nom: c.nom }))
      : [];
  const data: Territoire = requete.data ?? {
    ...territoireInconnu(
      nomAttendu ?? 'Ensemble du Togo',
      zonesAttendues,
      !code ? 'region' : regionConnue ? 'prefecture' : 'zone',
    ),
    zone: code ?? null,
    niveau: !code ? null : regionConnue ? 'region' : null,
  };

  // Niveau de la zone ; une ancienne réponse sans niveau reste lisible pour une région connue.
  const niveau = data.niveau ?? (regionConnue ? 'region' : undefined);
  const nomZone = code ? data.perimetre : undefined;
  const ascendants = data.ascendants ?? [];
  const contexte = useCarteDeContexte(data, niveau, code, plageApi);

  const ouvrir =
    !vide || (!code && regions.length > 1)
      ? (l: LigneZone) => choisir(l.code, { historique: true })
      : undefined;
  const { visibles, vides } = lignesDuTableau(data.lignes ?? [], niveau, { masquerVides: !vide });
  const niveauxLignes = visibles.map((l) => l.niveau);
  // Pagination (beaucoup de cantons et de localités) : 20 lignes par défaut ; on revient à la page 1 en changeant
  // de zone (la page retenue ne vaut que pour la zone où elle a été choisie).
  const [taille, setTaille] = useState<TaillePage>(20);
  const [pageChoisie, setPageChoisie] = useState({ zone: code, page: 0 });
  const tranche = paginer(visibles, pageChoisie.zone === code ? pageChoisie.page : 0, taille);
  const preinscriptions = avecPreinscriptions(niveau);
  const regionsComptees = (data.lignes ?? []).filter((l) => !l.horsReferentiel).length;
  const totalNational =
    national.data && national.data.perimetre === 'Ensemble du Togo' ? national.data.inscriptions : undefined;
  const descendre = !!ouvrir && visibles.some(peutDescendre);
  const premier = visibles.find(peutDescendre);

  // Carte : nationale, de la région ouverte, ou de la région qui contient la zone (préfecture mise en évidence).
  const carte = !code
    ? {
        fond: CARTE_REGIONS,
        zone: { nom: 'Togo', chiffres: data },
        lignes: data.lignes ?? [],
        titreListe: 'Régions, du nord au sud',
        libelleCarte: 'Carte des régions du Togo, colorée selon le taux de NIU générés',
        libelleOuvrir: 'Voir ses préfectures',
        selection: undefined,
      }
    : !contexte.profonde
      ? {
          fond: nomZone ? carteRegion(nomZone) : undefined,
          zone: { nom: nomZone ?? code, chiffres: data },
          lignes: data.lignes ?? [],
          titreListe: 'Préfectures, du nord au sud',
          libelleCarte: `Carte de la région ${nomZone} et de ses préfectures, colorée selon le taux de NIU générés`,
          libelleOuvrir: 'Voir ses communes',
          selection: undefined,
        }
      : {
          fond: contexte.region ? carteRegion(contexte.region.nom) : undefined,
          zone: { nom: contexte.region?.nom ?? '', chiffres: contexte.regionData ?? CHIFFRES_INCONNUS },
          lignes: contexte.regionData?.lignes ?? [],
          titreListe: 'Préfectures, du nord au sud',
          libelleCarte: `Carte de la région ${contexte.region?.nom} : préfecture ${contexte.prefecture?.nom} mise en évidence, colorée selon le taux de NIU générés`,
          libelleOuvrir: 'Voir ses communes',
          selection: contexte.prefecture?.nom,
        };

  return (
    <section className="panneau bloc-pleine-largeur bloc-territoire" aria-labelledby="titre-territoire">
      <div className="territoire__entete">
        <div>
          <nav aria-label="Fil d’Ariane du territoire" className="fil-ariane">
            {code ? (
              <>
                <button
                  type="button"
                  className="fil-ariane__lien"
                  onClick={() => choisir(undefined, { historique: true })}
                >
                  Togo
                </button>
                {ascendants.map((a) => (
                  <span key={a.code} className="fil-ariane__etape">
                    <Chevron />
                    <button
                      type="button"
                      className="fil-ariane__lien"
                      onClick={() => choisir(a.code, { historique: true })}
                    >
                      {a.nom}
                    </button>
                  </span>
                ))}
                <Chevron />
                <span aria-current="location">{nomZone}</span>
              </>
            ) : (
              <span aria-current="location">Togo</span>
            )}
          </nav>
          <h2 id="titre-territoire" className="titre-bloc">
            {titreTerritoire(niveau, nomZone)}
          </h2>
          <p className="texte-2 bloc__sous-titre">
            Carte colorée selon le taux de NIU : part des inscriptions qui ont leur NIU.
            {descendre &&
              premier &&
              ` Cliquez sur ${!code ? 'une région' : `une ligne du tableau`} pour voir ${CONTENU[premier.niveau] ?? 'ses sous-zones'}.`}
          </p>
        </div>
        <dl className="territoire__chiffres" aria-label="Chiffres de la zone">
          <div>
            <dt>Inscriptions</dt>
            <dd className="chiffre territoire__valeur">{nf(data.inscriptions)}</dd>
            <dd className="texte-2">
              {!code
                ? `dans ${regionsComptees} régions`
                : totalNational !== undefined
                  ? `${pct(part(data.inscriptions, totalNational))} du total national`
                  : `${nomNiveau(niveau)} ${nomZone}`}
            </dd>
          </div>
          <div>
            <dt>NIU générés</dt>
            <dd className="chiffre territoire__valeur">{nf(data.niuGeneres)}</dd>
            <dd className="texte-2">{pct(tauxNiu(data))} des inscriptions</dd>
          </div>
        </dl>
      </div>

      {isPending && <p className="texte-2 etat-chargement">Chargement des chiffres…</p>}

      <div className="territoire__corps">
        <CarteTerritoire
          fond={carte.fond}
          zone={carte.zone}
          lignes={carte.lignes}
          titreListe={carte.titreListe}
          libelleCarte={carte.libelleCarte}
          libelleOuvrir={carte.libelleOuvrir}
          selection={carte.selection}
          onOuvrir={ouvrir}
        />

        <div className="territoire__tableau">
          <table className="tableau tableau-zones">
            <caption className="tableau-zones__titre">
              {legendeSousZones(niveau, nomZone, niveauxLignes)}
            </caption>
            <thead>
              <tr>
                <th scope="col">{enTeteNiveau(niveauxLignes)}</th>
                {preinscriptions && (
                  <th scope="col" className="tableau__nombre col-secondaire">
                    Pré-inscriptions
                  </th>
                )}
                <th scope="col" className="tableau__nombre">
                  Inscriptions
                </th>
                <th scope="col" className="tableau__nombre">
                  NIU générés
                </th>
                <th scope="col" className="tableau__nombre col-secondaire">
                  Rejets
                </th>
                <th scope="col" className="tableau__nombre col-secondaire">
                  Échoués
                </th>
                <th scope="col" className="tableau__nombre col-secondaire">
                  En cours
                </th>
                <th
                  scope="col"
                  className="tableau__nombre col-secondaire"
                  title="De la réception du paquet par MOSIP au NIU"
                >
                  Délai médian
                </th>
              </tr>
            </thead>
            <tbody>
              {tranche.lignes.map((l) => {
                const alerte = alerteRejet(l);
                const mele = new Set(niveauxLignes).size > 1;
                return (
                  <tr key={l.code}>
                    <th scope="row">
                      {ouvrir && peutDescendre(l) ? (
                        <button type="button" className="tableau-zones__ouvrir" onClick={() => ouvrir(l)}>
                          {l.nom}
                          <Chevron />
                        </button>
                      ) : (
                        <span className="tableau-zones__nom">{l.nom}</span>
                      )}
                      {mele && (
                        <span className="texte-2 tableau-zones__niveau"> ({nomNiveau(l.niveau)})</span>
                      )}
                    </th>
                    {preinscriptions && (
                      <td className="chiffre tableau__nombre col-secondaire">{nf(l.preinscriptions)}</td>
                    )}
                    <td className="chiffre tableau__nombre">{nf(l.inscriptions)}</td>
                    <td className="chiffre tableau__nombre">{nf(l.niuGeneres)}</td>
                    <td
                      className={`chiffre tableau__nombre col-secondaire${alerte ? ' tableau-zones__alerte' : ''}`}
                      title={`Taux de rejet : ${pct(tauxRejet(l))}`}
                    >
                      {alerte && (
                        <span className="alerte-rejet" aria-label="Taux de rejet élevé">
                          ▲{' '}
                        </span>
                      )}
                      {nf(l.rejetees)}
                      {alerte && <span className="tableau-zones__taux texte-2">{pct(tauxRejet(l))}</span>}
                    </td>
                    <td className="chiffre tableau__nombre col-secondaire">{nf(l.echouees)}</td>
                    <td className="chiffre tableau__nombre col-secondaire">{nf(l.enCours)}</td>
                    <td className="chiffre tableau__nombre col-secondaire">
                      {`${nf(l.delaiMedianH ?? INCONNUE)}\u00a0h`}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <Pagination
            page={tranche.page}
            pages={tranche.pages}
            debut={tranche.debut}
            fin={tranche.fin}
            total={tranche.total}
            taille={taille}
            quoi={nomPluriel(niveauxLignes)}
            onPage={(page) => setPageChoisie({ zone: code, page })}
            onTaille={(t) => {
              setTaille(t);
              setPageChoisie({ zone: code, page: 0 });
            }}
          />
          {visibles.length === 0 && (
            <p className="texte-2 tableau-zones__note">
              {niveau === 'centre'
                ? 'Un centre est le dernier niveau du territoire.'
                : 'Aucune inscription dans cette zone sur la période.'}
            </p>
          )}
          {vides.length > 0 && (
            <p className="texte-2 tableau-zones__note">
              Le tableau omet{' '}
              {compteZones(
                vides.length,
                vides.map((l) => l.niveau),
              )}{' '}
              sans inscription sur la période.
            </p>
          )}
          <p className="texte-2 tableau-zones__note note-secondaire">
            <span className="alerte-rejet" aria-hidden="true">
              ▲
            </span>{' '}
            Taux de rejet de {pct(SEUIL_ALERTE_REJET / 100)} ou plus (rejets rapportés aux inscriptions de la
            zone).
          </p>
          <p className="texte-2 tableau-zones__note">
            {preinscriptions
              ? 'Pré-inscriptions selon la préfecture de résidence déclarée ; inscriptions selon le centre d’enrôlement.'
              : 'Inscriptions selon le centre d’enrôlement (les pré-inscriptions ne sont situées qu’à la préfecture).'}
          </p>
          <p className="texte-2 tableau-zones__note note-secondaire">
            Délai médian : de la réception du paquet par MOSIP au NIU, en heures, pour les premières
            inscriptions dont le NIU a été généré sur la période.
          </p>
          {data.nonClassees > 0 && (
            <p className="alerte-donnees" role="note">
              {nf(data.nonClassees)} inscriptions ont un statut MOSIP sans correspondance validée : comptées
              dans les inscriptions, hors des colonnes de statut.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
