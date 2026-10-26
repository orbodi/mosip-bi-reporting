import { useDelais, useSynchronisation } from '../../api/enrolement';
import { CarteIndicateur } from '../../composants/blocs/Indicateur';
import { Panneau } from '../../composants/blocs/Panneau';
import { depuisApi } from '../../lib/blocsVides';
import { nf, part, pct } from '../../lib/format';
import { borneHauteDelaiH } from '../../lib/traitement';
import { usePlageApi } from '../../lib/usePlagePeriode';

const H = '\u00a0h';

/**
 * Bloc « Délais de traitement » : de la réception au NIU (délai médian, 9 sur 10), de l'enrôlement à la réception
 * (paquets reçus en moins de 24 h), paquets synchronisés pas encore reçus (GET /enrolement/delais et
 * /enrolement/synchronisation). National ; délais en heures. Valeur indisponible : 0.
 */
export function BlocDelais() {
  const { plage, prete } = usePlageApi('enrolement');
  const { data: delais } = useDelais(plage, prete);
  const { data: synchro } = useSynchronisation();

  const niu = delais?.receptionNiu;
  const reception = delais?.enrolementReception;
  const moins24h = depuisApi(reception?.moins24h);

  return (
    <Panneau
      id="titre-delais"
      titre="Délais de traitement"
      pastille={<span className="pastille-portee">{delais?.perimetre ?? 'Ensemble du Togo'}</span>}
      sousTitre="Paquets reçus depuis le début des enrôlements, délais en heures"
      className="bloc-pleine-largeur delais"
    >
      <div className="cartes-m cartes-m--3">
        <CarteIndicateur
          icone="chrono"
          nom="De la réception au NIU"
          valeur={nf(depuisApi(niu?.medianeH))}
          unite="h"
          detail={
            <>
              délai médian ; 9 sur 10 en moins de{' '}
              <strong className="chiffre">{`${nf(borneHauteDelaiH(niu?.centile90H))}${H}`}</strong>
            </>
          }
        />
        <CarteIndicateur
          icone="horloge"
          nom="De l’enrôlement à la réception"
          valeur={nf(moins24h)}
          detail={
            <>
              paquets reçus en moins de 24{H}, soit{' '}
              <strong>{pct(part(moins24h, depuisApi(reception?.paquets)))}</strong> des paquets reçus
            </>
          }
        />
        <CarteIndicateur
          icone="alerte"
          nom="Synchronisés, pas encore reçus"
          valeur={nf(depuisApi(synchro?.nonRecus))}
          detail={
            <>
              paquets, dont <strong className="chiffre">{nf(depuisApi(synchro?.plusDe7Jours))}</strong> depuis
              plus de 7 jours
            </>
          }
        />
      </div>
    </Panneau>
  );
}
