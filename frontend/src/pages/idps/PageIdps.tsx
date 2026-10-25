import { GraphiqueHebdo } from '../../composants/blocs/GraphiqueHebdo';
import { CarteIndicateur, GrandChiffre } from '../../composants/blocs/Indicateur';
import { Panneau } from '../../composants/blocs/Panneau';
import { Jauge, Legende, Repartition } from '../../composants/blocs/Repartition';
import { CARTE_REGIONS } from '../../composants/carte/fondsDeCarte';
import { Bandeau } from '../../composants/coque/Bandeau';
import { FiltresPage } from '../../composants/coque/FiltresPage';
import { INCONNUE, semainesVides } from '../../lib/blocsVides';
import { nf, pct, semaineFr } from '../../lib/format';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import { useFinPeriode } from '../../lib/usePlagePeriode';
import type { DefinitionPage } from '../pages';

const ETAPES = ['Personnalisation', 'Contrôle qualité', 'Supervision', 'Cartes imprimées'];
const TYPES_ERREUR = ['Supervision', 'Contrôle qualité', 'Personnalisation'];

/**
 * IDPS (maquette/pages/Idps.dc.html) : nouveau circuit d'impression, en pilote. Journaux IDPS pas encore raccordés :
 * mise en page de la maquette, indicateurs à 0 (décision du 20/10/2026).
 */
export function PageIdps({ page }: { page: DefinitionPage }) {
  const fin = useFinPeriode(page.source);
  const { regions } = useFiltreRegion();
  const annee = fin.slice(0, 4);
  const nomsRegions =
    regions.length > 1 ? regions.map((r) => r.nom) : CARTE_REGIONS.contours.map((c) => c.nom);

  return (
    <>
      <Bandeau titre={page.titre} source={page.source} filtres={<FiltresPage />} />
      <div className="contenu page-m">
        <Panneau
          id="titre-ordres"
          titre="Ordres d’impression"
          sousTitre="Nouveau circuit d’impression IDPS, en pilote : il ne compte pas les cartes de la page Impression des cartes."
          coins
          sansMarge
        >
          <div className="duo">
            <div className="duo__principal">
              <GrandChiffre valeur={nf(INCONNUE)} detail="ordres d’impression reçus depuis MOSIP" />
              <Repartition
                libelle="Répartition des ordres"
                parts={[
                  { libelle: 'Imprimés', valeur: INCONNUE, couleur: 'bleu' },
                  { libelle: 'En attente', valeur: INCONNUE, couleur: 'en-cours' },
                  { libelle: 'En erreur', valeur: INCONNUE, couleur: 'rouge' },
                ]}
              />
              <Legende
                elements={[
                  { libelle: 'Imprimés', couleur: 'bleu', note: pct(INCONNUE) },
                  { libelle: 'En attente', couleur: 'en-cours', note: pct(INCONNUE) },
                  { libelle: 'En erreur', couleur: 'rouge', note: pct(INCONNUE) },
                ]}
              />
            </div>
            <div className="duo__cartes">
              <div className="cartes-m cartes-m--3">
                <CarteIndicateur
                  icone="sablier"
                  nom="En attente"
                  valeur={nf(INCONNUE)}
                  detail={`${pct(INCONNUE)} des ordres reçus`}
                />
                <CarteIndicateur
                  icone="carteId"
                  nom="Cartes imprimées"
                  valeur={nf(INCONNUE)}
                  detail={`${pct(INCONNUE)} des ordres reçus`}
                />
                <CarteIndicateur
                  icone="alerte"
                  nom="Erreurs"
                  valeur={nf(INCONNUE)}
                  detail={`${pct(INCONNUE)} des ordres reçus`}
                />
              </div>
            </div>
          </div>
        </Panneau>

        <div className="rangee rangee--21">
          <Panneau
            id="titre-etapes"
            titre="Où les ordres échouent"
            sousTitre={`Étapes de production d’une carte, dans l’ordre, sur les ${nf(INCONNUE)} ordres reçus.`}
            aside={
              <Legende
                elements={[
                  { libelle: 'Ordres qui passent', couleur: 'bleu' },
                  { libelle: 'Erreurs', couleur: 'rouge' },
                ]}
              />
            }
          >
            <div
              className="tableau-m-defile"
              tabIndex={0}
              role="group"
              aria-label="Tableau, défilable horizontalement"
            >
              <table className="tableau-m">
                <caption className="visuellement-cache">Ordres et erreurs par étape</caption>
                <thead>
                  <tr>
                    <th scope="col">Étape</th>
                    <th scope="col">Ordres entrés</th>
                    <th scope="col" className="gauche">
                      Sur les {nf(INCONNUE)} ordres reçus
                    </th>
                    <th scope="col">Erreurs</th>
                  </tr>
                </thead>
                <tbody>
                  {ETAPES.map((e) => (
                    <tr key={e}>
                      <th scope="row">{e}</th>
                      <td>{nf(INCONNUE)}</td>
                      <td className="gauche etape__barre">
                        <Repartition
                          libelle={`${e} : ordres qui passent et erreurs`}
                          parts={[
                            { libelle: 'Passent', valeur: INCONNUE, couleur: 'bleu' },
                            { libelle: 'Erreurs', valeur: INCONNUE, couleur: 'rouge' },
                          ]}
                        />
                      </td>
                      <td>{nf(INCONNUE)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panneau>
          <Panneau
            id="titre-types-erreur"
            titre="Erreurs par type"
            sousTitre={`${nf(INCONNUE)} erreurs au total sur la période.`}
          >
            <table className="classement">
              <caption className="visuellement-cache">Erreurs par type</caption>
              <tbody>
                {TYPES_ERREUR.map((t, i) => (
                  <tr key={t}>
                    <td className="classement__rang">{i + 1}</td>
                    <th scope="row">
                      <span className="classement__nom">{t}</span>
                      <span className="classement__lieu">Dernière : –</span>
                    </th>
                    <td className="erreur__jauge">
                      <Jauge valeur={INCONNUE} max={1} couleur="rouge" />
                    </td>
                    <td>
                      <span className="classement__valeur chiffre">{nf(INCONNUE)}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panneau>
        </div>

        <div className="rangee rangee--11">
          <Panneau
            id="titre-idps-regions"
            titre="Ordres et erreurs par région"
            sousTitre="Régions du nord au sud."
          >
            <div
              className="tableau-m-defile"
              tabIndex={0}
              role="group"
              aria-label="Tableau, défilable horizontalement"
            >
              <table className="tableau-m">
                <caption className="visuellement-cache">Ordres et erreurs par région</caption>
                <thead>
                  <tr>
                    <th scope="col">Région</th>
                    <th scope="col">Reçus</th>
                    <th scope="col">En attente</th>
                    <th scope="col">Imprimés</th>
                    <th scope="col">Erreurs</th>
                  </tr>
                </thead>
                <tbody>
                  {nomsRegions.map((r) => (
                    <tr key={r}>
                      <th scope="row">{r}</th>
                      <td>{nf(INCONNUE)}</td>
                      <td>{nf(INCONNUE)}</td>
                      <td>{nf(INCONNUE)}</td>
                      <td>{nf(INCONNUE)}</td>
                    </tr>
                  ))}
                  <tr className="total">
                    <th scope="row">Togo</th>
                    <td>{nf(INCONNUE)}</td>
                    <td>{nf(INCONNUE)}</td>
                    <td>{nf(INCONNUE)}</td>
                    <td>{nf(INCONNUE)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </Panneau>
          <Panneau
            id="titre-idps-semaines"
            titre={`Ordres et erreurs par semaine, ${annee}`}
            sousTitre={`Semaines de l’année ${annee} incluses dans la période.`}
            aside={
              <Legende
                elements={[
                  { libelle: 'Ordres reçus', couleur: 'serie-1' },
                  { libelle: 'Erreurs', couleur: 'rouge' },
                ]}
              />
            }
          >
            <GraphiqueHebdo
              semaines={semainesVides(fin, ['recus', 'erreurs'])}
              axeMois
              libelle="Ordres reçus et erreurs par semaine"
              series={[
                { cle: 'recus', libelle: 'Ordres reçus', couleur: 'serie-1', type: 'barre' },
                { cle: 'erreurs', libelle: 'Erreurs', couleur: 'rouge', type: 'barre' },
              ]}
              lecture={(s) =>
                `Semaine ${semaineFr(s.lundi)} : ${nf(s.valeurs.recus)} ordres reçus, ${nf(s.valeurs.erreurs)} erreurs.`
              }
            />
          </Panneau>
        </div>
      </div>
    </>
  );
}
