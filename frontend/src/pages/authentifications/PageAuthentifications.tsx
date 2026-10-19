import { GraphiqueHebdo } from '../../composants/blocs/GraphiqueHebdo';
import { Drapeau } from '../../composants/blocs/Icone';
import { CarteIndicateur, GrandChiffre } from '../../composants/blocs/Indicateur';
import { NoteSource } from '../../composants/blocs/NoteSource';
import { Panneau } from '../../composants/blocs/Panneau';
import { Legende, Repartition } from '../../composants/blocs/Repartition';
import { Bandeau } from '../../composants/coque/Bandeau';
import { FiltresPage } from '../../composants/coque/FiltresPage';
import { INCONNUE, semainesVides } from '../../lib/blocsVides';
import { jourMoisFr } from '../../lib/format';
import { useFinPeriode, usePlagePeriode } from '../../lib/usePlagePeriode';
import type { DefinitionPage } from '../pages';

const TYPES = ['Biométrique', 'Code à usage unique', 'Démographique', 'Combinée'];

/**
 * Authentifications (maquette/pages/Usage.dc.html). Base mosip_ida pas encore raccordée : mise en page de la
 * maquette, chiffres « – ». Les causes d'échec (A-CAUSE) restent à définir avec les codes d'erreur IDA.
 */
export function PageAuthentifications({ page }: { page: DefinitionPage }) {
  const fin = useFinPeriode(page.source);
  const { choix } = usePlagePeriode(page.source);

  return (
    <>
      <Bandeau titre={page.titre} source={page.source} filtres={<FiltresPage />} />
      <div className="contenu page-m">
        <Panneau id="titre-requetes" titre="Requêtes d’authentification" coins sansMarge>
          <div className="duo">
            <div className="duo__principal">
              <NoteSource source="Authentifications (mosip_ida)" />
              <GrandChiffre valeur="–" detail="requêtes de vérification d’identité reçues" />
              <Repartition
                libelle="Requêtes réussies et échouées"
                parts={[
                  { libelle: 'Réussies', valeur: INCONNUE, couleur: 'serie-1' },
                  { libelle: 'Échouées', valeur: INCONNUE, couleur: 'rouge' },
                ]}
              />
              <Legende
                elements={[
                  { libelle: 'Réussies', couleur: 'serie-1' },
                  { libelle: 'Échouées', couleur: 'rouge' },
                ]}
              />
            </div>
            <div className="duo__cartes">
              <div className="cartes-m cartes-m--3">
                <CarteIndicateur icone="personneOk" nom="Réussies" valeur="–" detail="– des requêtes" />
                <CarteIndicateur icone="croix" nom="Échouées" valeur="–" detail="– des requêtes" />
                <CarteIndicateur icone="empreinte" nom="Biométriques" valeur="–" detail="– des requêtes" />
                <CarteIndicateur
                  icone="telephone"
                  nom="Code à usage unique"
                  valeur="–"
                  detail="– des requêtes"
                />
                <CarteIndicateur
                  icone="carteId"
                  nom="Démographiques et combinées"
                  valeur="–"
                  detail="– des requêtes"
                />
                <CarteIndicateur
                  icone="immeuble"
                  nom="Partenaires raccordés"
                  valeur="–"
                  detail="Partenaire principal : –"
                />
              </div>
            </div>
          </div>
        </Panneau>

        <div className="rangee rangee--21">
          <Panneau
            id="titre-types-auth"
            titre="Par type d’authentification"
            sousTitre="Requêtes et échecs pour chaque type."
          >
            <div
              className="tableau-m-defile"
              tabIndex={0}
              role="group"
              aria-label="Tableau, défilable horizontalement"
            >
              <table className="tableau-m">
                <caption className="visuellement-cache">
                  Requêtes et échecs par type d’authentification
                </caption>
                <thead>
                  <tr>
                    <th scope="col">Type</th>
                    <th scope="col">Requêtes</th>
                    <th scope="col">Part</th>
                    <th scope="col">Échecs</th>
                    <th scope="col">Taux d’échec</th>
                  </tr>
                </thead>
                <tbody>
                  {TYPES.map((t) => (
                    <tr key={t}>
                      <th scope="row">{t}</th>
                      <td>–</td>
                      <td>–</td>
                      <td>–</td>
                      <td>–</td>
                    </tr>
                  ))}
                  <tr className="total">
                    <th scope="row">Total</th>
                    <td>–</td>
                    <td>–</td>
                    <td>–</td>
                    <td>–</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="note-m">
              <Drapeau />
              Taux d’échec de 50 % ou plus. Codes MOSIP des types : BIO, OTP, DEMO et MULTIPLE.
            </p>
          </Panneau>
          <Panneau
            id="titre-causes"
            titre="Causes des échecs"
            sousTitre="– échecs, du plus fréquent au moins fréquent."
          >
            <p className="non-disponible-m">
              Non disponible : les codes d’erreur de l’authentification (IDA) restent à exposer et à regrouper
              en causes lisibles.
            </p>
          </Panneau>
        </div>

        <Panneau
          id="titre-requetes-semaine"
          titre="Requêtes par semaine"
          sousTitre={
            choix === 'tout'
              ? '12 dernières semaines complètes.'
              : '12 semaines complètes jusqu’à la fin de la période.'
          }
          aside={
            <Legende
              elements={[
                { libelle: 'Réussies', couleur: 'serie-1' },
                { libelle: 'Échouées', couleur: 'rouge' },
              ]}
            />
          }
        >
          <GraphiqueHebdo
            semaines={semainesVides(fin, ['reussies', 'echouees'])}
            hauteur={260}
            libelle="Requêtes réussies et échouées par semaine"
            series={[
              { cle: 'reussies', libelle: 'Réussies', couleur: 'serie-1', type: 'pile' },
              { cle: 'echouees', libelle: 'Échouées', couleur: 'rouge', type: 'pile' },
            ]}
            lecture={(s) => `Semaine du ${jourMoisFr(s.lundi)} : chiffres indisponibles.`}
          />
        </Panneau>
      </div>
    </>
  );
}
