package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « Où s'arrêtent les paquets » de la page Enrôlement (I5, I6) : paquets rejetés et échoués par étape d'arrêt,
 * au jour de réception, dans l'ordre du traitement. Les étapes de moins de 1 %
 * du total sont regroupées en « Autres étapes » (code null), en dernier.
 * Contrôles : somme des rejets = rejetees, somme des échecs = echouees du bloc « Devenir » (même zone, même période).
 *
 * @param perimetre    « Ensemble du Togo » ou nom de la zone
 * @param du           première date incluse (jour de réception), ou null depuis le début
 * @param au           dernière date incluse, ou null jusqu'à la dernière donnée
 * @param totalRejets  paquets rejetés
 * @param totalEchecs  paquets échoués
 * @param rejets       étapes d'arrêt des paquets rejetés
 * @param echecs       étapes d'arrêt des paquets échoués
 */
public record ArretsParEtape(String perimetre, LocalDate du, LocalDate au, long totalRejets, long totalEchecs,
                             List<Etape> rejets, List<Etape> echecs) {

    /**
     * Une étape d'arrêt.
     *
     * @param code         code MOSIP de l'étape (VALIDATE_PACKET…, REFUS_POSTE), null pour « Autres étapes »
     * @param libelle      libellé français (seeds/ref_regprc_etapes.csv)
     * @param inscriptions paquets arrêtés à cette étape
     */
    public record Etape(String code, String libelle, long inscriptions) {
    }
}
