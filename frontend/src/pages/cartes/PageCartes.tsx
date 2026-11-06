import {
  useAnnulations,
  useAttenteCartes,
  useImpression,
  useSemainesCartes,
  useTerritoireCartes,
  useTopCentresCartes,
} from '../../api/cartes';
import type { LigneZoneCartes } from '../../api/client';
import { BarresHorizontales } from '../../composants/blocs/BarresHorizontales';
import { Classement } from '../../composants/blocs/Classement';
import { GraphiqueHebdo } from '../../composants/blocs/GraphiqueHebdo';
import { Chevron, Drapeau } from '../../composants/blocs/Icone';
import { CarteIndicateur, GrandChiffre } from '../../composants/blocs/Indicateur';
import { Panneau } from '../../composants/blocs/Panneau';
import { Legende, Repartition } from '../../composants/blocs/Repartition';
import { CarteZones } from '../../composants/carte/CarteZones';
import { CARTE_REGIONS, carteRegion } from '../../composants/carte/fondsDeCarte';
import { Bandeau } from '../../composants/coque/Bandeau';
import { FiltresPage } from '../../composants/coque/FiltresPage';
import { INCONNUE } from '../../lib/blocsVides';
import {
  CLASSES_A_REMETTRE,
  alerteARemettre,
  barresAttente,
  chiffresImpression,
  classeARemettre,
  lectureARemettre,
  noteAttente,
  noteRejeteesAnnulees,
  partARemettre,
  semainesCartes,
  texteAnnulees,
  texteModesRemise,
} from '../../lib/cartes';
import { dateFr, nf, part, pct, semaineFr } from '../../lib/format';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import { useFinPeriode, usePlageApi } from '../../lib/usePlagePeriode';
import type { DefinitionPage } from '../pages';
import './cartes.css';

/**
 * Impression des cartes (maquette/pages/Cartes.dc.html), lot 8 : tables printing_* de MOSIP (GET /api/v1/cartes/…).
 * Commandes au jour de réception, cartes au jour d'expédition (lecture cohorte, décision du 03/11/2026). Seul le bloc
 * géographique suit le filtre Région (?region=) ; les autres blocs sont nationaux.
 */
export function PageCartes({ page }: { page: DefinitionPage }) {
  const { plage, prete, choix } = usePlageApi(page.source);
  const fin = useFinPeriode(page.source);
  const { region, regions, code, choisir } = useFiltreRegion();

  const impression = useImpression(plage, prete);
  const annulations = useAnnulations(plage, prete);
  const semainesApi = useSemainesCartes(plage, prete);
  const territoire = useTerritoireCartes(plage, code, prete);
  const attente = useAttenteCartes(plage, prete);
  const centres = useTopCentresCartes(plage, prete);

  const c = chiffresImpression(impression.data);
  const semaines = semainesCartes(semainesApi.data, fin);
  const sousTitreSemaines =
    choix === 'tout'
      ? '12 dernières semaines complètes.'
      : '12 semaines complètes jusqu’à la fin de la période.';

  // Bloc géographique : lignes de l'API (régions, ou préfectures de la région ouverte) ; sans réponse, les zones de la
  // carte sans chiffres.
  const t = territoire.data;
  const fond = region ? carteRegion(region.nom) : CARTE_REGIONS;
  const zonesConnues = t?.lignes ?? [];
  const zonesVides: LigneZoneCartes[] = (
    region
      ? (fond?.contours ?? []).map((z) => ({ code: z.nom, nom: z.nom }))
      : regions.length
        ? regions
        : CARTE_REGIONS.contours.map((z) => ({ code: z.nom, nom: z.nom }))
  ).map((z) => ({
    ...z,
    niveau: region ? 'prefecture' : 'region',
    horsReferentiel: false,
    ouvrable: !region,
    expediees: INCONNUE,
    remises: INCONNUE,
    aRemettre: INCONNUE,
  }));
  const zones: LigneZoneCartes[] = zonesConnues.length ? zonesConnues : zonesVides;
  const totaux = t ?? { expediees: INCONNUE, remises: INCONNUE, aRemettre: INCONNUE };
  const nomZone = region?.nom ?? 'Togo';
  const ouvrables = !region && regions.length > 1;

  const lignesCentres = centres.data?.centres.length
    ? centres.data.centres.map((x) => ({
        cle: x.code,
        nom: x.nom,
        lieu: [x.prefecture, x.region].filter(Boolean).join(', '),
        valeur: nf(x.remises),
        detail: `${pct(part(x.remises, x.expediees))} des ${nf(x.expediees)} cartes expédiées`,
      }))
    : [1, 2, 3, 4, 5].map((n) => ({
        cle: String(n),
        nom: '–',
        lieu: '–',
        valeur: nf(INCONNUE),
        detail: `${pct(INCONNUE)} des ${nf(INCONNUE)} cartes expédiées`,
      }));

  return (
    <>
      <Bandeau titre={page.titre} source={page.source} filtres={<FiltresPage source="cartes" />} />
      <div className="contenu page-m">
        <Panneau id="titre-impression" titre="Impression et remise" coins sansMarge>
          <div className="impression">
            <div className="duo">
              <div className="duo__principal">
                <GrandChiffre
                  valeur={nf(c.remises)}
                  detail={`cartes remises, soit ${pct(part(c.remises, c.expediees))} des ${nf(c.expediees)} cartes expédiées`}
                />
                <Repartition
                  libelle="Cartes remises et à remettre"
                  parts={[
                    { libelle: 'Remises', valeur: c.remises, couleur: 'bleu' },
                    { libelle: 'À remettre', valeur: c.aRemettre, couleur: 'en-cours' },
                  ]}
                />
                <Legende
                  elements={[
                    { libelle: 'Remises', couleur: 'bleu', note: pct(part(c.remises, c.expediees)) },
                    { libelle: 'À remettre', couleur: 'en-cours', note: pct(part(c.aRemettre, c.expediees)) },
                  ]}
                />
                <p className="note-m note-m--filet impression__modes">{texteModesRemise(c)}</p>
              </div>
              <div className="duo__cartes">
                <div role="group" aria-labelledby="titre-groupe-cartes">
                  <h3 id="titre-groupe-cartes" className="impression__groupe">
                    Cartes
                  </h3>
                  <div className="cartes-m cartes-m--3">
                    <CarteIndicateur
                      icone="imprimante"
                      nom="Imprimées et expédiées"
                      valeur={nf(c.expediees)}
                      detail={`${pct(part(c.expediees, c.demandes))} des demandes`}
                    />
                    <CarteIndicateur
                      icone="carteHorloge"
                      nom="Cartes à remettre"
                      valeur={nf(c.aRemettre)}
                      detail={`${pct(part(c.aRemettre, c.expediees))} des cartes expédiées`}
                    />
                    <CarteIndicateur
                      icone="chrono"
                      nom="Délai du NIU à la carte"
                      valeur={`${nf(c.delaiMedianJours)} jours`}
                      detail="Médiane, sur les cartes remises"
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className="impression__demandes">
              <div role="group" aria-labelledby="titre-groupe-demandes">
                <h3 id="titre-groupe-demandes" className="impression__groupe">
                  Demandes
                </h3>
                <div className="cartes-m cartes-m--5">
                  <CarteIndicateur
                    icone="document"
                    nom="Demandes d’impression"
                    valeur={nf(c.demandes)}
                    detail={`dont ${nf(c.envoyees)} envoyées à l’imprimeur`}
                  />
                  <CarteIndicateur
                    icone="sablier"
                    nom="En attente d’impression"
                    valeur={nf(c.enAttente)}
                    detail="Pas encore envoyées à l’imprimeur"
                  />
                  <CarteIndicateur
                    icone="croix"
                    nom="Demandes rejetées"
                    valeur={nf(c.rejetees)}
                    detail={
                      c.derniereRejetee
                        ? `Dernière reçue le ${dateFr(c.derniereRejetee)}`
                        : 'Aucune sur la période'
                    }
                  />
                  <CarteIndicateur
                    icone="documentAnnule"
                    nom="Demandes annulées"
                    valeur={nf(c.annulees)}
                    detail={texteAnnulees(annulations.data?.motifs)}
                  />
                  <CarteIndicateur
                    icone="alerte"
                    nom="Erreurs d’envoi à l’IDPS"
                    valeur={nf(c.erreursIdps)}
                    detail={
                      c.derniereErreurIdps
                        ? `Parmi les demandes ; dernière reçue le ${dateFr(c.derniereErreurIdps)}`
                        : 'Parmi les demandes'
                    }
                  />
                </div>
              </div>
            </div>
          </div>
        </Panneau>

        <div className="rangee rangee--21">
          <Panneau
            id="titre-impressions-semaine"
            titre="Impressions par semaine"
            sousTitre={sousTitreSemaines}
            aside={
              <Legende
                elements={[
                  { libelle: 'Cartes imprimées', couleur: 'serie-1' },
                  { libelle: 'Demandes d’impression', couleur: 'vert', ligne: true },
                ]}
              />
            }
          >
            <GraphiqueHebdo
              semaines={semaines}
              hauteur={280}
              libelle="Cartes imprimées et demandes d’impression par semaine"
              series={[
                { cle: 'imprimees', libelle: 'Cartes imprimées', couleur: 'serie-1', type: 'barre' },
                { cle: 'demandes', libelle: 'Demandes d’impression', couleur: 'vert', type: 'courbe' },
              ]}
              lecture={(s) =>
                `Semaine ${semaineFr(s.lundi)} : ${nf(s.valeurs.imprimees)} cartes imprimées, ${nf(s.valeurs.demandes)} demandes d’impression.`
              }
            />
          </Panneau>
          <Panneau
            id="titre-rejets-semaine"
            titre="Rejetées et annulées par semaine"
            sousTitre="Mêmes semaines, au jour de réception de la demande."
            aside={
              <Legende
                elements={[
                  { libelle: 'Rejetées', couleur: 'rouge' },
                  { libelle: 'Annulées', couleur: 'orange' },
                ]}
              />
            }
          >
            <GraphiqueHebdo
              semaines={semaines}
              hauteur={240}
              ton="rouge"
              libelle="Demandes d’impression rejetées et annulées par semaine"
              series={[
                { cle: 'rejetees', libelle: 'Rejetées', couleur: 'rouge', type: 'pile' },
                { cle: 'annulees', libelle: 'Annulées', couleur: 'orange', type: 'pile' },
              ]}
              lecture={(s) =>
                `Semaine ${semaineFr(s.lundi)} : ${nf(s.valeurs.rejetees)} rejetées, ${nf(s.valeurs.annulees)} annulées.`
              }
            />
            <p className="note-m note-m--filet">{noteRejeteesAnnulees(semaines)}</p>
          </Panneau>
        </div>

        <Panneau
          id="titre-a-remettre"
          titre={region ? `Cartes à remettre : ${region.nom}` : 'Cartes à remettre par région'}
          surTitre={
            region ? (
              <span className="fil-ariane">
                <button
                  type="button"
                  className="fil-ariane__lien"
                  onClick={() => choisir(undefined, { historique: true })}
                >
                  Togo
                </button>
                <Chevron taille={11} />
                <span aria-current="location">{region.nom}</span>
              </span>
            ) : undefined
          }
          sousTitre={
            region
              ? 'Carte colorée selon la part des cartes expédiées qui restent à remettre, par préfecture.'
              : 'Carte colorée selon la part des cartes expédiées qui restent à remettre. Cliquez sur une région pour voir ses préfectures.'
          }
        >
          <dl className="chiffres-zone">
            <div>
              <dt>Cartes expédiées</dt>
              <dd className="chiffre">{nf(totaux.expediees)}</dd>
              <dd>{region ? region.nom : 'Ensemble du Togo'}</dd>
            </div>
            <div>
              <dt>Remises</dt>
              <dd className="chiffre">{nf(totaux.remises)}</dd>
              <dd>{pct(part(totaux.remises, totaux.expediees))} des expédiées</dd>
            </div>
            <div>
              <dt>À remettre</dt>
              <dd className="chiffre">{nf(totaux.aRemettre)}</dd>
              <dd>{pct(part(totaux.aRemettre, totaux.expediees))} des expédiées</dd>
            </div>
          </dl>
          <div className="geo-m">
            <CarteZones
              fond={fond}
              zone={{
                nom: nomZone,
                valeur: pct(partARemettre(totaux)),
                lecture: lectureARemettre(nomZone, totaux),
              }}
              zones={zones.map((z) => ({
                code: z.code,
                nom: z.nom,
                valeur: pct(partARemettre(z)),
                classe: classeARemettre(partARemettre(z)),
                lecture: lectureARemettre(z.nom, z),
                ouvrable: ouvrables && z.ouvrable && !z.horsReferentiel,
              }))}
              titreListe={region ? 'Préfectures, du nord au sud' : 'Régions, du nord au sud'}
              libelleCarte={
                region
                  ? `Carte de la région ${region.nom} et de ses préfectures, colorée selon la part des cartes à remettre`
                  : 'Carte des régions du Togo, colorée selon la part des cartes expédiées à remettre'
              }
              legende={{
                titre: 'Part des cartes expédiées à remettre',
                libelles: CLASSES_A_REMETTRE.map((x) => x.libelle),
              }}
              onOuvrir={(z) => choisir(z, { historique: true })}
            />
            <div
              className="tableau-m-defile"
              tabIndex={0}
              role="group"
              aria-label="Tableau, défilable horizontalement"
            >
              <table className="tableau-m">
                <caption>{region ? 'Préfectures' : 'Régions'}</caption>
                <thead>
                  <tr>
                    <th scope="col">{region ? 'Préfecture' : 'Région'}</th>
                    <th scope="col">Expédiées</th>
                    <th scope="col">Remises</th>
                    <th scope="col">À remettre</th>
                    <th scope="col">Part à remettre</th>
                  </tr>
                </thead>
                <tbody>
                  {zones.map((z) => (
                    <tr key={z.code}>
                      <th scope="row">
                        {ouvrables && z.ouvrable && !z.horsReferentiel ? (
                          <button
                            type="button"
                            className="bouton-zone"
                            onClick={() => choisir(z.code, { historique: true })}
                          >
                            {z.nom}
                            <Chevron />
                          </button>
                        ) : (
                          z.nom
                        )}
                      </th>
                      <td>{nf(z.expediees)}</td>
                      <td>{nf(z.remises)}</td>
                      <td>{nf(z.aRemettre)}</td>
                      <td>
                        {alerteARemettre(z) && (
                          <Drapeau libelle="Alerte : plus de la moitié reste à remettre" />
                        )}
                        {pct(partARemettre(z))}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="note-m">
                <Drapeau />
                Plus de la moitié des cartes expédiées reste à remettre.
              </p>
            </div>
          </div>
        </Panneau>

        <div className="rangee rangee--2">
          <Panneau
            id="titre-attente"
            titre="Depuis quand ces cartes attendent"
            sousTitre="Cartes à remettre, selon le temps écoulé depuis l’expédition."
          >
            <BarresHorizontales
              libelle="Cartes à remettre par ancienneté"
              elements={barresAttente(attente.data)}
            />
            <p className="note-m note-m--filet">{noteAttente(attente.data)}</p>
          </Panneau>
          <Panneau
            id="titre-top-centres-cartes"
            titre="Top des centres"
            sousTitre="Ensemble du Togo, classés par nombre de cartes remises"
          >
            <Classement
              titre="Top des centres par cartes remises"
              colonneNom="Centre"
              colonneValeur="Cartes remises"
              lignes={lignesCentres}
            />
          </Panneau>
        </div>
      </div>
    </>
  );
}
