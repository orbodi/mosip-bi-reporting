import { Icone } from '../../composants/blocs/Icone';
import { CarteIndicateur, GrandChiffre } from '../../composants/blocs/Indicateur';
import { NoteSource } from '../../composants/blocs/NoteSource';
import { Panneau } from '../../composants/blocs/Panneau';
import { Jauge, Legende, Repartition } from '../../composants/blocs/Repartition';
import { Bandeau } from '../../composants/coque/Bandeau';
import { FiltresPage } from '../../composants/coque/FiltresPage';
import { INCONNUE } from '../../lib/blocsVides';
import type { DefinitionPage } from '../pages';
import './abis.css';

const DOIGTS = ['Pouce', 'Index', 'Majeur', 'Annulaire', 'Auriculaire'];

function TableMain({ titre }: { titre: string }) {
  return (
    <div>
      <h4 className="h4-m">{titre}</h4>
      <div
        className="tableau-m-defile"
        tabIndex={0}
        role="group"
        aria-label="Tableau, défilable horizontalement"
      >
        <table className="tableau-m">
          <caption className="visuellement-cache">Qualité par doigt, {titre.toLowerCase()}</caption>
          <thead>
            <tr>
              <th scope="col">Doigt</th>
              <th scope="col" className="gauche">
                Faible · Moyen · Excellent
              </th>
              <th scope="col">Exploitables</th>
              <th scope="col">NBPK</th>
              <th scope="col">Score</th>
            </tr>
          </thead>
          <tbody>
            {DOIGTS.map((d) => (
              <tr key={d}>
                <th scope="row">{d}</th>
                <td className="gauche">
                  <Repartition
                    libelle={`${d} : faible, moyen, excellent`}
                    parts={[
                      { libelle: 'Faible', valeur: INCONNUE, couleur: 'orange' },
                      { libelle: 'Moyen', valeur: INCONNUE, couleur: 'bleu-clair' },
                      { libelle: 'Excellent', valeur: INCONNUE, couleur: 'bleu' },
                    ]}
                  />
                </td>
                <td>–</td>
                <td>–</td>
                <td>–</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Score({
  icone,
  nom,
  sur,
  detail,
  yeux,
}: {
  icone: string;
  nom: string;
  sur: number;
  detail: string;
  yeux?: boolean;
}) {
  return (
    <div className="indicateur indicateur--score">
      <Icone nom={icone} />
      <div className="indicateur__corps">
        <span className="indicateur__nom">{nom}</span>
        <span className="score">
          <b className="chiffre">–</b>
          <span>sur {sur}</span>
        </span>
        <Jauge valeur={INCONNUE} max={sur} />
        <span className="indicateur__detail">{detail}</span>
        {yeux && (
          <div className="yeux">
            {['Œil droit', 'Œil gauche'].map((oeil) => (
              <div key={oeil}>
                <span>{oeil}</span>
                <Jauge valeur={INCONNUE} max={100} couleur="serie-1" />
                <b className="chiffre">–</b>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * ABIS (maquette/pages/Biometrie.dc.html) : transactions, adjudication, erreurs, qualité biométrique. Journaux
 * IN Groupe pas encore raccordés : mise en page de la maquette, chiffres « – ».
 */
export function PageAbis({ page }: { page: DefinitionPage }) {
  return (
    <>
      <Bandeau titre={page.titre} source={page.source} filtres={<FiltresPage />} />
      <div className="contenu page-m">
        <Panneau
          id="titre-transactions"
          titre="Transactions ABIS"
          sousTitre="Requêtes envoyées par MOSIP à l’ABIS."
          coins
        >
          <NoteSource source="ABIS (journaux IN Groupe)" />
          <div className="cartes-m cartes-m--2 abis__transactions">
            <CarteIndicateur
              taille="grande"
              icone="basePlus"
              nom="Requêtes d’insertion"
              valeur="–"
              detail="Enregistrement des biométries dans la base de l’ABIS"
            />
            <CarteIndicateur
              taille="grande"
              icone="loupe"
              nom="Requêtes de déduplication"
              valeur="–"
              detail="Recherche de doublons dans la base de l’ABIS"
            />
          </div>
          <p className="note-m note-m--filet">Source : journaux d’audit des nœuds de l’ABIS.</p>
        </Panneau>

        <Panneau
          id="titre-adjudication"
          titre="Adjudication"
          sousTitre="Dossiers envoyés par MOSIP à l’adjudication, où un agent tranche entre doublon et non-doublon."
          sansMarge
        >
          <div className="duo">
            <div className="duo__principal">
              <GrandChiffre valeur="–" unite="requêtes d’adjudication reçues par l’ABIS" />
              <Repartition
                libelle="Répartition des requêtes d’adjudication"
                parts={[
                  { libelle: 'HIT', valeur: INCONNUE, couleur: 'rouge' },
                  { libelle: 'NO HIT', valeur: INCONNUE, couleur: 'serie-1' },
                  { libelle: 'En attente', valeur: INCONNUE, couleur: 'en-cours' },
                  { libelle: 'En erreur', valeur: INCONNUE, couleur: 'orange' },
                ]}
              />
              <Legende
                elements={[
                  { libelle: 'HIT', couleur: 'rouge' },
                  { libelle: 'NO HIT', couleur: 'serie-1' },
                  { libelle: 'En attente', couleur: 'en-cours' },
                  { libelle: 'En erreur', couleur: 'orange' },
                ]}
              />
              <p className="note-m note-m--filet">
                En attente : requêtes reçues, moins les cas traités et les requêtes en erreur.
              </p>
            </div>
            <div className="duo__cartes">
              <div className="cartes-m cartes-m--2">
                <CarteIndicateur
                  icone="dossierOk"
                  nom="Cas d’adjudication traités"
                  valeur="–"
                  detail="– des requêtes reçues"
                />
                <CarteIndicateur
                  icone="sablier"
                  nom="Dossiers en attente de traitement"
                  valeur="–"
                  detail="– des requêtes reçues"
                />
                <CarteIndicateur
                  icone="doublon"
                  nom="Dossiers traités avec statut HIT"
                  valeur="–"
                  detail="Doublon confirmé : – des cas traités"
                />
                <CarteIndicateur
                  icone="personneOk"
                  nom="Dossiers traités NO HIT"
                  valeur="–"
                  detail="Aucun doublon : – des cas traités"
                />
              </div>
            </div>
          </div>
        </Panneau>

        <Panneau
          id="titre-erreurs-abis"
          titre="Erreurs ABIS"
          sousTitre="Réponses en erreur renvoyées par l’ABIS à MOSIP, par type de requête."
          sansMarge
        >
          <div className="duo">
            <div className="duo__principal">
              <GrandChiffre valeur="–" unite="réponses en erreur" />
              <Repartition
                libelle="Erreurs par type de requête"
                parts={[
                  { libelle: 'Insertion', valeur: INCONNUE, couleur: 'rouge-fonce' },
                  { libelle: 'Identification', valeur: INCONNUE, couleur: 'rouge' },
                  { libelle: 'Adjudication', valeur: INCONNUE, couleur: 'orange' },
                ]}
              />
              <Legende
                elements={[
                  { libelle: 'Insertion', couleur: 'rouge-fonce' },
                  { libelle: 'Identification', couleur: 'rouge' },
                  { libelle: 'Adjudication', couleur: 'orange' },
                ]}
              />
            </div>
            <div className="duo__cartes">
              <div className="cartes-m cartes-m--3">
                <CarteIndicateur
                  icone="basePlus"
                  nom="Erreurs d’insertion"
                  valeur="–"
                  detail="– des requêtes d’insertion"
                />
                <CarteIndicateur
                  icone="loupe"
                  nom="Erreurs d’identification"
                  valeur="–"
                  detail="– des requêtes de déduplication"
                />
                <CarteIndicateur
                  icone="balance"
                  nom="Erreurs d’adjudication"
                  valeur="–"
                  detail="– des requêtes d’adjudication"
                />
              </div>
            </div>
          </div>
        </Panneau>

        <Panneau
          id="titre-qualite"
          titre="Qualité des données biométriques"
          sousTitre="Score qualité moyen des biométries injectées dans l’ABIS."
        >
          <div className="qualite">
            <Score icone="visage" nom="Face" sur={255} detail="Score moyen" />
            <Score icone="oeil" nom="Iris" sur={100} detail="Score moyen des deux yeux" yeux />
            <Score icone="empreinte" nom="Fingerprint" sur={255} detail="Moyenne des 10 doigts" />
          </div>

          <div className="note-m--filet qualite__doigts">
            <h3 className="h3-m">Fingerprint : niveau de qualité et taux d’exploitabilité</h3>
            <p className="panneau-m__sous-titre">
              Niveau de chaque doigt capturé selon son nombre de minuties (NBPK).
            </p>
            <div className="exploitables">
              <div>
                <div className="exploitables__valeur chiffre">–</div>
                <p className="grand-chiffre__detail">
                  des doigts capturés sont exploitables (niveau moyen ou excellent)
                </p>
              </div>
              <div className="exploitables__repartition">
                <Repartition
                  libelle="Niveaux de qualité des doigts"
                  parts={[
                    { libelle: 'Faible', valeur: INCONNUE, couleur: 'orange' },
                    { libelle: 'Moyen', valeur: INCONNUE, couleur: 'bleu-clair' },
                    { libelle: 'Excellent', valeur: INCONNUE, couleur: 'bleu' },
                  ]}
                />
                <Legende
                  elements={[
                    { libelle: 'Faible', couleur: 'orange', note: '–' },
                    { libelle: 'Moyen', couleur: 'bleu-clair', note: '–' },
                    { libelle: 'Excellent', couleur: 'bleu', note: '–' },
                  ]}
                />
                <p className="note-m">
                  Faible : moins de 16 minuties (sous le minimum recommandé à l’enrôlement, ISO/IEC 19794-2) ·
                  Moyen : 16 à 39 · Excellent : 40 et plus.
                </p>
              </div>
            </div>
            <h3 className="h3-m qualite__titre-doigts">Taux d’exploitabilité par doigt</h3>
            <div className="mains">
              <TableMain titre="Main droite" />
              <TableMain titre="Main gauche" />
            </div>
            <p className="note-m note-m--filet">
              Source : journaux qualité des nœuds de capture (requêtes d’identification).
            </p>
          </div>
        </Panneau>
      </div>
    </>
  );
}
