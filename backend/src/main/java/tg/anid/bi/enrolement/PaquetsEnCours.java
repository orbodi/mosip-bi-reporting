package tg.anid.bi.enrolement;

import java.time.OffsetDateTime;
import java.util.List;

/**
 * Paquets en cours de traitement par étape (I7), à l'heure du dernier calcul : « dont bloqués » = dernière
 * transaction il y a plus de {@code seuilJours} jours. Stock, sans période. Mêmes regroupements que
 * {@link ArretsParEtape}. Contrôle : total = enCours du bloc « Devenir » sans période, sur la même zone.
 *
 * @param perimetre  « Ensemble du Togo » ou nom de la zone
 * @param calculeLe  heure du calcul du stock (passage dbt), null tant que rien n'est publié
 * @param seuilJours ancienneté au-delà de laquelle un paquet est dit bloqué (30)
 * @param total      paquets en cours
 * @param bloques    dont bloqués
 * @param etapes     étapes, dans l'ordre du traitement
 */
public record PaquetsEnCours(String perimetre, OffsetDateTime calculeLe, int seuilJours, long total, long bloques,
                             List<Etape> etapes) {

    /**
     * Une étape et ses paquets en cours.
     *
     * @param code         code MOSIP de l'étape, null pour « Autres étapes »
     * @param libelle      libellé français
     * @param inscriptions paquets en cours à cette étape
     * @param bloques      dont bloqués
     */
    public record Etape(String code, String libelle, long inscriptions, long bloques) {
    }
}
