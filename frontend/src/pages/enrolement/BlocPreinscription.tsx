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
 * Bloc « Pré-inscription » (maquette Enrôlement) : demandes de pré-enrôlement, rendez-vous, attente, expirées,
 * honorées à l'inscription et dernière demande (GET /api/v1/enrolement/preinscriptions, décision du 20/10/2026).
 * National : une pré-inscription n'a pas de territoire, la pastille le signale quand le filtre Région est actif.
 * Valeur indisponible (null de l'API) : 0 à l'écran ; « Femmes pré-inscrites » n'a pas de source.
 */
export function BlocPreinscription() {
  const { actif } = useFiltreRegion();
  const { plage, prete } = usePlageApi('enrolement');
  const { data } = usePreinscriptions(plage, prete);

  const demandes = depuisApi(data?.demandes);
  const reserves = depuisApi(data?.rendezVousReserves);
  const enAttente = depuisApi(data?.enAttenteRendezVous);
  const expirees = depuisApi(data?.expirees);
  const honorees = depuisApi(data?.honorees);
  const femmes = depuisApi(data?.femmes);
  const hommes = depuisApi(data?.hommes);
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
            <CarteIndicateur icone="calendrierX" nom="Expirées" valeur={nf(expirees)} />
            <CarteIndicateur
              icone="personneOk"
              nom="Honorées à l’inscription"
              valeur={nf(honorees)}
              detail={`${pct(part(honorees, demandes))} des demandes`}
            />
            <CarteIndicateur
              icone="personnes"
              nom="Femmes pré-inscrites"
              valeur={nf(femmes)}
              detail={`${pct(part(femmes, demandes))}, contre ${nf(hommes)} hommes`}
            />
            <CarteIndicateur
              icone="horloge"
              nom="Dernière demande"
              valeur={derniere ? dateFr(derniere) : '–'}
              detail={derniere ? `à ${heureFr(derniere)}` : undefined}
            />
          </div>
        </div>
      </div>
    </Panneau>
  );
}
