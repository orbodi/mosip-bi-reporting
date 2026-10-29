package tg.anid.bi.enrolement;

import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « Inscriptions et NIU par jour » de la page Enrôlement (décision du 29/10/2026) : les 28 derniers jours, du
 * plus ancien à aujourd'hui (heure du Togo), le jour en cours compris. Le front les montre par pages de 7 jours,
 * aujourd'hui et les 6 jours précédents d'abord. Inscriptions comptées au jour de réception, NIU au jour de
 * génération (bi.fait_niu_jour). National.
 *
 * @param perimetre      « Ensemble du Togo »
 * @param aujourdhui     dernier jour de la liste : la date du jour au Togo
 * @param niuDisponibles faux tant que bi.fait_niu_jour n'est pas alimentée : les NIU valent alors 0
 * @param jours          28 jours, du plus ancien au plus récent ; un jour sans donnée vaut 0
 */
public record InscriptionsParJour(String perimetre, LocalDate aujourdhui, boolean niuDisponibles, List<Jour> jours) {

    /**
     * Un jour.
     *
     * @param jour         date (heure du Togo)
     * @param inscriptions inscriptions reçues ce jour-là
     * @param niuGeneres   NIU générés ce jour-là
     */
    @Schema(name = "JourInscriptions")
    public record Jour(LocalDate jour, long inscriptions, long niuGeneres) {
    }
}
