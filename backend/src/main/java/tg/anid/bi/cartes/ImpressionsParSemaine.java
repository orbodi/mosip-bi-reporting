package tg.anid.bi.cartes;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

/**
 * Blocs « Impressions par semaine » et « Rejetées et annulées par semaine » : les 12 semaines complètes (lundi à
 * dimanche) qui finissent au plus tard à la fin de la période, ou à la dernière donnée d'impression. Demandes,
 * rejetées et annulées au jour de réception de la commande ; cartes imprimées (expédiées) au jour d'expédition.
 *
 * @param perimetre « Ensemble du Togo » ou nom de la zone filtrée
 * @param du        première date de la période, ou null
 * @param au        dernière date de la période, ou null
 * @param semaines  de la plus ancienne à la plus récente ; vide tant que la source n'est pas alimentée
 */
public record ImpressionsParSemaine(String perimetre, LocalDate du, LocalDate au, List<Semaine> semaines) {

    /**
     * Une semaine.
     *
     * @param lundi        premier jour de la semaine
     * @param dansPeriode  vrai si la semaine a au moins un jour dans la période
     * @param demandes     commandes reçues
     * @param expediees    cartes imprimées et expédiées
     * @param rejetees     commandes reçues cette semaine-là et rejetées
     * @param annulees     commandes reçues cette semaine-là et annulées (parmi les demandes)
     */
    @Schema(name = "SemaineImpression")
    public record Semaine(LocalDate lundi, boolean dansPeriode, long demandes, long expediees, long rejetees,
                          long annulees) {
    }
}
