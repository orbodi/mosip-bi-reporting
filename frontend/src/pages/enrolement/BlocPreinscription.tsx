import { usePreinscriptions } from '../../api/enrolement';
import { CarteIndicateur, GrandChiffre } from '../../composants/blocs/Indicateur';
import { Panneau } from '../../composants/blocs/Panneau';
import { Legende, Repartition } from '../../composants/blocs/Repartition';
import { depuisApi } from '../../lib/blocsVides';
import { dateFr, heureFr, nf, part, pct } from '../../lib/format';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import { usePlageApi } from '../../lib/usePlagePeriode';
import { PastillePortee } from './PastillePortee';

/**
 * Bloc « Pré-inscription » (maquette Enrôlement) : demandes de pré-enrôlement, rendez-vous, attente, femmes,
 * hommes et dernière demande (GET /api/v1/enrolement/preinscriptions).
 * National : une pré-inscription n'a pas de territoire, la pastille le signale quand le filtre Région est actif.
 * Valeur indisponible (null de l'API) : 0 à l'écran. Femmes et hommes : part parmi les demandes au sexe connu ; une
 * note signale les demandes dont le sexe n'est pas encore connu (enrichissement en cours).
 */
export function BlocPreinscription() {
  const { actif } = useFiltreRegion();
  const { plage, prete } = usePlageApi('enrolement');
  const { data } = usePreinscriptions(plage, prete);

  const demandes = depuisApi(data?.demandes);
  const reserves = depuisApi(data?.rendezVousReserves);
  const enAttente = depuisApi(data?.enAttenteRendezVous);
  const femmes = depuisApi(data?.femmes);
  const hommes = depuisApi(data?.hommes);
  const sexeConnu = femmes + hommes;
  const nonClassees = data?.nonClassees ?? 0;
  const derniere = data?.derniereDemande;

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
          {nonClassees > 0 && (
            <p className="alerte-donnees" role="note">
              {nf(nonClassees)} demandes ont un statut MOSIP sans correspondance validée : elles sont comptées
              dans les demandes, hors des statuts.
            </p>
          )}
          {sexeConnu > 0 && sexeConnu < demandes && (
            <p className="alerte-donnees" role="note">
              Sexe connu pour {nf(sexeConnu)} demandes sur {nf(demandes)} ({pct(part(sexeConnu, demandes))}) :
              celui des autres n’est pas encore renseigné.
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
            <CarteIndicateur
              icone="femme"
              nom="Femmes pré-inscrites"
              valeur={nf(femmes)}
              detail={`${pct(part(femmes, sexeConnu))} des sexes connus`}
            />
            <CarteIndicateur
              icone="homme"
              nom="Hommes pré-inscrits"
              valeur={nf(hommes)}
              detail={`${pct(part(hommes, sexeConnu))} des sexes connus`}
            />
          </div>
        </div>
      </div>
    </Panneau>
  );
}
