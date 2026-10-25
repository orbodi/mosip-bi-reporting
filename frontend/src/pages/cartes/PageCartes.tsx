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
import { INCONNUE, semainesVides } from '../../lib/blocsVides';
import { nf, pct, semaineFr } from '../../lib/format';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import { useFinPeriode, usePlagePeriode } from '../../lib/usePlagePeriode';
import type { DefinitionPage } from '../pages';

/**
 * Impression des cartes (maquette/pages/Cartes.dc.html). Source credential / partenaires d'impression et de
 * distribution pas encore raccordée : mise en page de la maquette, indicateurs à 0 (décision du 20/10/2026).
 */
export function PageCartes({ page }: { page: DefinitionPage }) {
  const fin = useFinPeriode(page.source);
  const { choix } = usePlagePeriode(page.source);
  const { region, regions, regional, choisir } = useFiltreRegion();
  const semaines = semainesVides(fin, ['imprimees', 'demandes', 'rejetees']);
  const sousTitreSemaines =
    choix === 'tout'
      ? '12 dernières semaines complètes.'
      : '12 semaines complètes jusqu’à la fin de la période.';

  const zones = region
    ? (carteRegion(region.nom)?.contours ?? []).map((c) => ({ code: c.nom, nom: c.nom }))
    : regions.length > 1
      ? regions
      : CARTE_REGIONS.contours.map((c) => ({ code: c.nom, nom: c.nom }));
  const nomZone = region?.nom ?? 'Togo';

  return (
    <>
      <Bandeau titre={page.titre} source={page.source} filtres={<FiltresPage />} />
      <div className="contenu page-m">
        <Panneau id="titre-impression" titre="Impression et remise" coins sansMarge>
          <div className="duo">
            <div className="duo__principal">
              <GrandChiffre
                valeur={nf(INCONNUE)}
                detail={`cartes remises, soit ${pct(INCONNUE)} des ${nf(INCONNUE)} cartes expédiées`}
              />
              <Repartition
                libelle="Cartes remises et à remettre"
                parts={[
                  { libelle: 'Remises', valeur: INCONNUE, couleur: 'bleu' },
                  { libelle: 'À remettre', valeur: INCONNUE, couleur: 'en-cours' },
                ]}
              />
              <Legende
                elements={[
                  { libelle: 'Remises', couleur: 'bleu', note: pct(INCONNUE) },
                  { libelle: 'À remettre', couleur: 'en-cours', note: pct(INCONNUE) },
                ]}
              />
            </div>
            <div className="duo__cartes">
              <div className="cartes-m cartes-m--3">
                <CarteIndicateur
                  icone="document"
                  nom="Demandes d’impression"
                  valeur={nf(INCONNUE)}
                  detail={`${pct(INCONNUE)} des NIU générés`}
                />
                <CarteIndicateur
                  icone="sablier"
                  nom="En attente d’impression"
                  valeur={nf(INCONNUE)}
                  detail="Pas encore lancées en production"
                />
                <CarteIndicateur
                  icone="croix"
                  nom="Demandes rejetées"
                  valeur={nf(INCONNUE)}
                  detail="Dernière : –"
                />
                <CarteIndicateur
                  icone="imprimante"
                  nom="Imprimées et expédiées"
                  valeur={nf(INCONNUE)}
                  detail={`${pct(INCONNUE)} des demandes`}
                />
                <CarteIndicateur
                  icone="carteHorloge"
                  nom="Cartes à remettre"
                  valeur={nf(INCONNUE)}
                  detail={`${pct(INCONNUE)} des cartes expédiées`}
                />
                <CarteIndicateur
                  icone="chrono"
                  nom="Délai du NIU à la carte"
                  valeur={`${nf(INCONNUE)} jours`}
                  detail="Médiane, sur les cartes remises"
                />
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
            titre="Demandes rejetées par semaine"
            sousTitre="Mêmes semaines."
          >
            <GraphiqueHebdo
              semaines={semaines}
              hauteur={240}
              ton="rouge"
              libelle="Demandes d’impression rejetées par semaine"
              series={[{ cle: 'rejetees', libelle: 'Demandes rejetées', couleur: 'rouge', type: 'barre' }]}
              lecture={(s) => `Semaine ${semaineFr(s.lundi)} : ${nf(s.valeurs.rejetees)} demandes rejetées.`}
            />
            <p className="note-m note-m--filet">{nf(INCONNUE)} demande rejetée sur la période.</p>
          </Panneau>
        </div>

        <Panneau
          id="titre-a-remettre"
          titre={region ? `Cartes à remettre : ${region.nom}` : 'Cartes à remettre par région'}
          surTitre={
            region && !regional ? (
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
              <dd className="chiffre">{nf(INCONNUE)}</dd>
              <dd>{region ? region.nom : 'Ensemble du Togo'}</dd>
            </div>
            <div>
              <dt>Remises</dt>
              <dd className="chiffre">{nf(INCONNUE)}</dd>
              <dd>{pct(INCONNUE)} des expédiées</dd>
            </div>
            <div>
              <dt>À remettre</dt>
              <dd className="chiffre">{nf(INCONNUE)}</dd>
              <dd>{pct(INCONNUE)} des expédiées</dd>
            </div>
          </dl>
          <div className="geo-m">
            <CarteZones
              fond={region ? carteRegion(region.nom) : CARTE_REGIONS}
              zone={{
                nom: nomZone,
                valeur: pct(INCONNUE),
                lecture: `${nomZone} : ${pct(INCONNUE)} des cartes expédiées à remettre`,
              }}
              zones={zones.map((z) => ({
                code: z.code,
                nom: z.nom,
                valeur: pct(INCONNUE),
                classe: -1,
                lecture: `${z.nom} : ${pct(INCONNUE)} des cartes expédiées à remettre`,
                ouvrable: !region && !regional && regions.length > 1,
              }))}
              titreListe={region ? 'Préfectures, du nord au sud' : 'Régions, du nord au sud'}
              libelleCarte={
                region
                  ? `Carte de la région ${region.nom} et de ses préfectures, colorée selon la part des cartes à remettre`
                  : 'Carte des régions du Togo, colorée selon la part des cartes expédiées à remettre'
              }
              legende={{
                titre: 'Part des cartes expédiées à remettre',
                libelles: ['< 35 %', '35 à 45 %', '45 à 52 %', '52 % et +'],
              }}
              onOuvrir={(c) => choisir(c, { historique: true })}
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
                        {!region && !regional && regions.length > 1 ? (
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
                      <td>{nf(INCONNUE)}</td>
                      <td>{nf(INCONNUE)}</td>
                      <td>{nf(INCONNUE)}</td>
                      <td>{pct(INCONNUE)}</td>
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
              elements={[
                { libelle: 'Moins de 30 jours', valeur: INCONNUE, couleur: 'bleu-pale' },
                { libelle: '30 à 90 jours', valeur: INCONNUE, couleur: 'bleu-clair' },
                { libelle: '90 à 180 jours', valeur: INCONNUE, couleur: 'serie-1' },
                { libelle: 'Plus de 180 jours', valeur: INCONNUE, couleur: 'bleu-fonce' },
              ]}
            />
            <p className="note-m note-m--filet">
              {nf(INCONNUE)} cartes, soit {pct(INCONNUE)} des cartes à remettre, attendent depuis plus de six
              mois.
            </p>
          </Panneau>
          <Panneau
            id="titre-top-centres-cartes"
            titre="Top des centres"
            sousTitre={`${region ? region.nom : 'Ensemble du Togo'}, classés par nombre de cartes remises`}
          >
            <Classement
              titre="Top des centres par cartes remises"
              colonneNom="Centre"
              colonneValeur="Cartes remises"
              lignes={[1, 2, 3, 4, 5].map((n) => ({
                cle: String(n),
                nom: '–',
                lieu: '–',
                valeur: nf(INCONNUE),
                detail: `${pct(INCONNUE)} des ${nf(INCONNUE)} cartes expédiées`,
              }))}
            />
          </Panneau>
        </div>
      </div>
    </>
  );
}
