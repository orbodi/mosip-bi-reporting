import { Link } from '@tanstack/react-router';
import type { CSSProperties } from 'react';
import { useUsagers } from '../../api/authentifications';
import { useImpression, useTerritoireCartes } from '../../api/cartes';
import { useDevenirInscriptions, usePreinscriptions, useTerritoire } from '../../api/enrolement';
import { CarteZones } from '../../composants/carte/CarteZones';
import { CARTE_REGIONS } from '../../composants/carte/fondsDeCarte';
import { Chevron, Icone } from '../../composants/blocs/Icone';
import { CarteIndicateur } from '../../composants/blocs/Indicateur';
import { Panneau } from '../../composants/blocs/Panneau';
import { Bandeau } from '../../composants/coque/Bandeau';
import { FiltresPage } from '../../composants/coque/FiltresPage';
import { chiffresUsagers } from '../../lib/authentifications';
import { INCONNUE, depuisApi, devenirInconnu } from '../../lib/blocsVides';
import {
  CLASSES_AVEC_CARTE,
  chiffresImpression,
  classeAvecCarte,
  moinsDeLaMoitie,
  texteNiuSansCommande,
} from '../../lib/cartes';
import { nf, part, pct } from '../../lib/format';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import { usePlageApi } from '../../lib/usePlagePeriode';
import type { DefinitionPage } from '../pages';
import './vue-ensemble.css';

interface Etape {
  nom: string;
  libelle: string;
  icone: string;
  valeur: number;
  /** Part des inscriptions affichée sous le nombre (sauf pour les inscriptions elles-mêmes). */
  part: boolean;
}

const COULEURS_BANDES = ['bleu', 'bleu-vif', 'bleu', 'bleu-vif', 'bleu', 'bleu-vif', 'or'];

/**
 * Vue d'ensemble du parcours citoyen (maquette/pages/Main.dc.html). Les étapes d'enrôlement viennent de l'API
 * (blocs « Devenir des inscriptions » et « Pré-inscription »), les demandes, l'impression et la remise de l'API des
 * cartes (lot 8c, GET /api/v1/cartes/impression et /territoire), la carte Authentifications des requêtes des usagers
 * (GET /api/v1/authentifications/usagers, mêmes chiffres que la page, 07/11/2026) ; ABIS et IDPS attendent leurs
 * sources (0, décision du 20/10/2026).
 */
export function PageVueEnsemble({ page }: { page: DefinitionPage }) {
  const { plage, prete, choix } = usePlageApi(page.source);
  const { code, region, choisir } = useFiltreRegion();
  const devenir = useDevenirInscriptions(plage, prete);
  const d = devenir.data ?? devenirInconnu();
  const territoire = useTerritoire(plage, undefined, prete);
  const preinscriptions = usePreinscriptions(plage, prete);
  const cartes = chiffresImpression(useImpression(plage, prete).data);
  const cartesRegions = useTerritoireCartes(plage, undefined, prete);
  const toutes = choix === 'tout';
  // Authentifications : même choix de période, borné aux données de leur source (comme sur leur page).
  const periodeAuth = usePlageApi('authentifications');
  const auth = chiffresUsagers(useUsagers(periodeAuth.plage, periodeAuth.prete).data);

  const ins = d.inscriptions;
  const traites = d.niuGeneres + d.echouees + d.rejetees;
  const remises = cartes.remises;
  const etapes: Etape[] = [
    {
      nom: 'Pré-inscription',
      libelle: 'Pré-inscriptions',
      icone: 'calendrierOk',
      valeur: depuisApi(preinscriptions.data?.demandes),
      part: true,
    },
    { nom: 'Inscription', libelle: 'Inscriptions', icone: 'personne', valeur: ins, part: false },
    { nom: 'Traitement', libelle: 'Paquets traités', icone: 'engrenage', valeur: traites, part: true },
    { nom: 'NIU', libelle: 'NIU générés', icone: 'carteOk', valeur: d.niuGeneres, part: true },
    { nom: 'Demande', libelle: 'Demandes d’impression', icone: 'document', valeur: cartes.demandes, part: true },
    {
      nom: 'Impression',
      libelle: 'Cartes imprimées et expédiées',
      icone: 'imprimante',
      valeur: cartes.expediees,
      part: true,
    },
    { nom: 'Remise', libelle: 'Cartes remises', icone: 'remise', valeur: remises, part: true },
  ];

  const regions = territoire.data?.lignes.filter((l) => !l.horsReferentiel) ?? [];
  const lignesRegions = regions.length
    ? regions
    : (CARTE_REGIONS.contours.map((c) => ({
        code: c.nom,
        nom: c.nom,
        inscriptions: INCONNUE,
        niuGeneres: INCONNUE,
      })) as {
        code: string;
        nom: string;
        inscriptions: number;
        niuGeneres: number;
      }[]);
  // Cartes remises de chaque région (même code que bi.zone), rapportées à ses inscriptions.
  const remisesRegion = new Map<string, number>(
    (cartesRegions.data?.lignes ?? []).map((l) => [l.code, l.remises] as const),
  );
  const avecCarte = (r: { code: string; inscriptions: number }) =>
    part(depuisApi(remisesRegion.get(r.code)), r.inscriptions);
  const partNationale = part(remises, ins);
  const lectureRegion = (nom: string, p: number) => `${nom} : ${pct(p)} des inscrits ont reçu leur carte`;

  return (
    <>
      <Bandeau
        titre={page.titre}
        source={page.source}
        sourcesMiseAJour={page.sourcesMiseAJour}
        filtres={<FiltresPage />}
      />
      <div className="contenu page-m">
        <section className="panneau-m parcours" aria-labelledby="titre-parcours">
          <span className="coin coin--hg" aria-hidden="true" />
          <span className="coin coin--hd" aria-hidden="true" />
          <span className="coin coin--bg" aria-hidden="true" />
          <span className="coin coin--bd" aria-hidden="true" />
          <div className="parcours__entete">
            <div>
              <div className="panneau-m__ligne-titre">
                <h2 id="titre-parcours" className="parcours__titre">
                  De la pré-inscription à la carte en main
                </h2>
              </div>
              <p className="panneau-m__sous-titre">Du rendez-vous à la remise de la carte, en sept étapes.</p>
            </div>
            <p className="parcours__chiffre-cle">
              <span className="chiffre">{nf(remises)}</span>
              <span>
                {toutes
                  ? `cartes en main, soit ${pct(part(remises, ins))} des inscrits`
                  : 'cartes remises sur la période'}
              </span>
            </p>
          </div>
          <ol className="frise">
            {etapes.map((e, i) => {
              const bas = i % 2 === 0;
              const derniere = i === etapes.length - 1;
              const ratio = part(e.valeur, ins);
              return (
                <li
                  key={e.nom}
                  className={`frise__etape ${bas ? 'frise__etape--bas' : 'frise__etape--haut'}`}
                  style={{ '--colonne': i + 1 } as CSSProperties}
                >
                  <div
                    className={`frise__bande frise__bande--${COULEURS_BANDES[i]}${i === 0 ? ' frise__bande--premiere' : ''}`}
                    aria-hidden="true"
                  >
                    <span className="frise__numero">{i + 1}</span>
                    {e.nom}
                  </div>
                  <div className="frise__repere" aria-hidden="true">
                    <span className={`frise__tige${derniere ? ' frise__tige--or' : ''}`} />
                    <span className={`frise__pastille${derniere ? ' frise__pastille--or' : ''}`}>
                      <Icone nom={e.icone} blanche taille={26} />
                    </span>
                  </div>
                  <div className="frise__texte">
                    <span className="frise__nom">
                      <span className={`frise__numero frise__numero--${COULEURS_BANDES[i]}`}>{i + 1}</span>
                      {e.nom}
                    </span>
                    <span className="frise__libelle">{e.libelle}</span>
                    <span className="frise__valeur chiffre">{nf(e.valeur)}</span>
                    {e.part && (
                      <span className="frise__part">
                        <span className="frise__piste" aria-hidden="true">
                          <span
                            className={derniere ? 'frise__piste--or' : undefined}
                            style={{ width: `${Number.isFinite(ratio) ? Math.min(ratio * 100, 100) : 0}%` }}
                          />
                        </span>
                        {pct(ratio)}
                      </span>
                    )}
                    {e.nom === 'Traitement' && (
                      <span className="frise__paquets">
                        <span>
                          <span>
                            <i className="couleur--en-cours" aria-hidden="true" />
                            En cours
                          </span>
                          <b className="chiffre">{nf(d.enCours)}</b>
                        </span>
                        <span>
                          <span>
                            <i className="couleur--orange" aria-hidden="true" />
                            Échoués
                          </span>
                          <b className="chiffre">{nf(d.echouees)}</b>
                        </span>
                        <span>
                          <span>
                            <i className="couleur--rouge" aria-hidden="true" />
                            Rejetés
                          </span>
                          <b className="chiffre">{nf(d.rejetees)}</b>
                        </span>
                      </span>
                    )}
                  </div>
                </li>
              );
            })}
          </ol>
          {texteNiuSansCommande(cartes) && (
            <p className="note-m parcours__note parcours__alerte">
              <Icone nom="alerte" taille={18} />
              <span>{texteNiuSansCommande(cartes)}</span>
            </p>
          )}
          {!toutes && (
            <p className="note-m parcours__note">
              Sur une période, chaque étape compte ce qui s’y est passé pendant la période : les cartes
              demandées, imprimées ou remises peuvent concerner des inscriptions plus anciennes, d’où des
              parts parfois supérieures à 100 %.
            </p>
          )}
        </section>

        <Panneau id="titre-modules" titre="Indicateurs clés par module" sansFilet>
          <div className="cartes-m cartes-m--3">
            <CarteIndicateur
              taille="module"
              lien="/enrolement"
              icone="inscription"
              nom="Enrôlement"
              valeur={nf(ins)}
              unite="inscriptions"
              detail={
                <>
                  <strong>{pct(part(d.niuGeneres, ins))}</strong> ont leur NIU, {nf(d.enCours)} en cours
                </>
              }
            />
            <CarteIndicateur
              taille="module"
              lien="/impression-cartes"
              icone="carteId"
              nom="Impression des cartes"
              valeur={nf(remises)}
              unite="cartes remises"
              detail={
                <>
                  <strong>{nf(cartes.aRemettre)}</strong> cartes expédiées encore à remettre
                </>
              }
            />
            <CarteIndicateur
              taille="module"
              lien="/abis"
              icone="empreinte"
              nom="ABIS"
              valeur={nf(INCONNUE)}
              unite="recherches de doublons"
              detail={
                <>
                  <strong>{pct(INCONNUE)}</strong> des inscriptions dédupliquées
                </>
              }
            />
            <CarteIndicateur
              taille="module"
              lien="/idps"
              icone="imprimante"
              nom="IDPS"
              valeur={nf(INCONNUE)}
              unite="ordres d’impression"
              detail={
                <>
                  <strong>{nf(INCONNUE)} en erreur</strong>, {nf(INCONNUE)} carte imprimée
                </>
              }
            />
            <CarteIndicateur
              taille="module"
              lien="/authentifications"
              icone="bouclier"
              nom="Authentifications"
              valeur={nf(auth.requetes)}
              unite="requêtes des usagers"
              detail={
                <>
                  <strong>{pct(part(auth.reussies, auth.requetes))}</strong> réussies,{' '}
                  {pct(part(auth.echouees, auth.requetes))} échouées
                </>
              }
            />
            <CarteIndicateur
              taille="module"
              lien="/exploration"
              icone="baseHorloge"
              nom="Exploration des données"
              valeur="24"
              unite="indicateurs à croiser"
              detail={
                <>
                  <strong>5 sources</strong>, par région, date, profil ou type
                </>
              }
            />
          </div>
        </Panneau>

        <Panneau
          id="titre-parcours-regions"
          titre="Le parcours par région"
          sousTitre={`Part des inscrits qui ont reçu leur carte, par région (moyenne nationale : ${pct(partNationale)}).`}
          aside={
            <Link to="/impression-cartes" search={(precedent) => precedent} className="lien-panneau">
              Détail des cartes par région <Chevron />
            </Link>
          }
        >
          <div className="geo-m">
            <CarteZones
              fond={CARTE_REGIONS}
              zone={{
                nom: 'Togo',
                valeur: pct(partNationale),
                lecture: lectureRegion('Togo', partNationale),
              }}
              zones={lignesRegions.map((r) => ({
                code: r.code,
                nom: r.nom,
                valeur: pct(avecCarte(r)),
                classe: classeAvecCarte(avecCarte(r)),
                lecture: lectureRegion(r.nom, avecCarte(r)),
                ouvrable: regions.length > 0,
              }))}
              titreListe="Régions, du nord au sud"
              libelleCarte="Carte des régions du Togo, colorée selon la part des inscrits ayant reçu leur carte"
              legende={{
                titre: 'Inscrits ayant reçu leur carte',
                libelles: CLASSES_AVEC_CARTE.map((c) => c.libelle),
              }}
              libelleOuvrir="Choisir cette région"
              selection={region?.nom}
              onOuvrir={(c) => choisir(c === code ? undefined : c)}
            />
            <div>
              <div
                className="tableau-m-defile"
                tabIndex={0}
                role="group"
                aria-label="Tableau, défilable horizontalement"
              >
                <table className="tableau-m">
                  <caption className="visuellement-cache">Le parcours par région</caption>
                  <thead>
                    <tr>
                      <th scope="col">Région</th>
                      <th scope="col">Inscriptions</th>
                      <th scope="col">NIU générés</th>
                      <th scope="col">Cartes remises</th>
                      <th scope="col">Inscrits avec carte</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...lignesRegions]
                      .sort((a, b) => (b.inscriptions || 0) - (a.inscriptions || 0))
                      .map((r) => (
                        <tr key={r.code} className={region?.code === r.code ? 'choisie' : undefined}>
                          <th scope="row">{r.nom}</th>
                          <td>{nf(r.inscriptions)}</td>
                          <td>{nf(r.niuGeneres)}</td>
                          <td>{nf(depuisApi(remisesRegion.get(r.code)))}</td>
                          <td>
                            {moinsDeLaMoitie(avecCarte(r)) ? (
                              <strong>{pct(avecCarte(r))}</strong>
                            ) : (
                              pct(avecCarte(r))
                            )}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
              <p className="note-m">En gras : régions où moins de 50 % des inscrits ont reçu leur carte.</p>
            </div>
          </div>
        </Panneau>
      </div>
    </>
  );
}
