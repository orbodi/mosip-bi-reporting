import { CarteIndicateur, GrandChiffre } from '../../composants/blocs/Indicateur';
import { Panneau } from '../../composants/blocs/Panneau';
import { Legende, Repartition } from '../../composants/blocs/Repartition';
import { INCONNUE } from '../../lib/blocsVides';
import { nf, part, pct } from '../../lib/format';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import { PastillePortee } from './PastillePortee';

/**
 * Bloc « Pré-inscription » (maquette Enrôlement). Source en attente de décision (docs/plans/enrolement.md, P1) :
 * mise en page de la maquette, indicateurs à 0 tant qu'ils sont indisponibles (décision du 20/10/2026).
 */
export function BlocPreinscription() {
  const { actif } = useFiltreRegion();
  const demandes = INCONNUE;
  const reserves = INCONNUE;
  const enAttente = INCONNUE;
  const femmes = INCONNUE;
  const hommes = INCONNUE;

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
            <CarteIndicateur icone="calendrierX" nom="Expirées" valeur={nf(INCONNUE)} />
            <CarteIndicateur icone="personneOk" nom="Honorées à l’inscription" valeur={nf(INCONNUE)} />
            <CarteIndicateur
              icone="personnes"
              nom="Femmes pré-inscrites"
              valeur={nf(femmes)}
              detail={`${pct(part(femmes, demandes))}, contre ${nf(hommes)} hommes`}
            />
            <CarteIndicateur icone="horloge" nom="Dernière demande" valeur="–" />
          </div>
        </div>
      </div>
    </Panneau>
  );
}
