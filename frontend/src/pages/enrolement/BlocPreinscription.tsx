import { CarteIndicateur, GrandChiffre } from '../../composants/blocs/Indicateur';
import { NoteSource } from '../../composants/blocs/NoteSource';
import { Panneau } from '../../composants/blocs/Panneau';
import { Legende, Repartition } from '../../composants/blocs/Repartition';
import { INCONNUE } from '../../lib/blocsVides';
import { nf, part, pct } from '../../lib/format';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import { PastillePortee } from './PastillePortee';

/**
 * Bloc « Pré-inscription » (maquette Enrôlement). Source en attente de décision (docs/plans/enrolement.md, P1) :
 * mise en page de la maquette, chiffres « – ». Les règles connues sont déjà affichées : expirations non mesurables
 * (date de rendez-vous inexploitable), honorées non mesurées, sexe non disponible.
 */
export function BlocPreinscription() {
  const { actif } = useFiltreRegion();
  const demandes = INCONNUE;
  const reserves = INCONNUE;
  const enAttente = INCONNUE;

  return (
    <Panneau
      id="titre-preinscription"
      titre="Pré-inscription"
      pastille={actif ? <PastillePortee /> : undefined}
      className="bloc-pleine-largeur"
      sansMarge
    >
      <div className="duo">
        <div className="duo__principal">
          <NoteSource source="Pré-inscription" />
          <GrandChiffre valeur={nf(demandes)} unite="demandes de pré-enrôlement" />
          <Repartition
            libelle="Rendez-vous réservé et en attente de rendez-vous"
            parts={[
              { libelle: 'Rendez-vous réservé', valeur: reserves, couleur: 'bleu' },
              { libelle: 'En attente de rendez-vous', valeur: enAttente, couleur: 'bleu-clair' },
            ]}
          />
          <Legende
            elements={[
              { libelle: 'Rendez-vous réservé', couleur: 'bleu', note: pct(part(reserves, demandes)) },
              {
                libelle: 'En attente de rendez-vous',
                couleur: 'bleu-clair',
                note: pct(part(enAttente, demandes)),
              },
            ]}
          />
        </div>
        <div className="duo__cartes">
          <div className="cartes-m cartes-m--3">
            <CarteIndicateur
              icone="calendrierOk"
              nom="Rendez-vous réservé"
              valeur={nf(reserves)}
              detail="Estimation"
            />
            <CarteIndicateur
              icone="sablier"
              nom="En attente de rendez-vous"
              valeur={nf(enAttente)}
              detail={`${pct(part(enAttente, demandes))} des demandes`}
            />
            <CarteIndicateur
              icone="calendrierX"
              nom="Expirées"
              valeur={nf(INCONNUE)}
              detail="Non mesurables : date de rendez-vous inexploitable (31/12/9999)"
            />
            <CarteIndicateur
              icone="personneOk"
              nom="Honorées à l’inscription"
              valeur="–"
              detail="Non mesuré : rendez-vous et inscriptions non reliés"
            />
            <CarteIndicateur
              icone="personnes"
              nom="Femmes pré-inscrites"
              valeur="–"
              detail="Non disponible : sexe sans source anonymisée"
            />
            <CarteIndicateur icone="horloge" nom="Dernière demande" valeur="–" />
          </div>
        </div>
      </div>
    </Panneau>
  );
}
