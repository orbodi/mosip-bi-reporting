import { usePreinscriptions } from '../../api/enrolement';
import { CarteIndicateur, GrandChiffre } from '../../composants/blocs/Indicateur';
import { Panneau } from '../../composants/blocs/Panneau';
import { Legende, Repartition } from '../../composants/blocs/Repartition';
import { depuisApi } from '../../lib/blocsVides';
import { dateFr, heureFr, nf, part, pct } from '../../lib/format';
import { usePlageApi } from '../../lib/usePlagePeriode';

/**
 * Bloc « Pré-inscription » (maquette Enrôlement) : demandes de pré-enrôlement, rendez-vous, attente, femmes,
 * hommes et dernière demande (GET /api/v1/enrolement/preinscriptions).
 * National : une pré-inscription n'a pas de territoire.
 * Valeur indisponible (null de l'API) : 0 à l'écran.
 */
export function BlocPreinscription() {
  const { plage, prete } = usePlageApi('enrolement');
  const { data } = usePreinscriptions(plage, prete);

  const demandes = depuisApi(data?.demandes);
  const reserves = depuisApi(data?.rendezVousReserves);
  const enAttente = depuisApi(data?.enAttenteRendezVous);
  const femmes = depuisApi(data?.femmes);
  const hommes = depuisApi(data?.hommes);
  const nonClassees = data?.nonClassees ?? 0;
  const derniere = data?.derniereDemande;

  return (
    <Panneau id="titre-preinscription" titre="Pré-inscription" className="bloc-pleine-largeur" sansMarge>
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
          {nonClassees > 0 && (
            <p className="alerte-donnees" role="note">
              {nf(nonClassees)} demandes ont un statut MOSIP sans correspondance validée : elles sont comptées
              dans les demandes, hors des statuts.
            </p>
          )}
        </div>
        <div className="duo__cartes">
          <div className="cartes-m cartes-m--3">
            <CarteIndicateur
              icone="calendrierOk"
              nom="Rendez-vous réservé"
              valeur={nf(reserves)}
              detail={`${pct(part(reserves, demandes))} des demandes`}
            />
            <CarteIndicateur
              icone="sablier"
              nom="En attente de rendez-vous"
              valeur={nf(enAttente)}
              detail={`${pct(part(enAttente, demandes))} des demandes`}
            />
            <CarteIndicateur
              icone="horloge"
              nom="Dernière demande"
              valeur={derniere ? dateFr(derniere) : '–'}
              detail={derniere ? `à ${heureFr(derniere)}` : undefined}
            />
            <CarteIndicateur icone="femme" nom="Femmes pré-inscrites" valeur={nf(femmes)} />
            <CarteIndicateur icone="homme" nom="Hommes pré-inscrits" valeur={nf(hommes)} />
          </div>
        </div>
      </div>
    </Panneau>
  );
}
