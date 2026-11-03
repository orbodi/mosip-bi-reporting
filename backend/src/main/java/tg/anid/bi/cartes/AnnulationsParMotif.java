package tg.anid.bi.cartes;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

/**
 * Commandes d'impression annulées (I-ANN), comptées à part (décision du 02/11/2026), par motif : même lecture que les
 * demandes (jour de réception de la commande). Contrôle : somme des motifs = total = annulées du bloc « Impression et
 * remise ».
 *
 * @param perimetre « Ensemble du Togo » ou nom de la zone
 * @param du        première date incluse, ou null
 * @param au        dernière date incluse, ou null
 * @param total     commandes annulées
 * @param motifs    du plus fréquent au moins fréquent (à égalité, par libellé)
 */
public record AnnulationsParMotif(String perimetre, LocalDate du, LocalDate au, long total, List<Motif> motifs) {

    /**
     * Un motif.
     *
     * @param code     code MOSIP (CANCEL_PHOTO…) ou NON_REPERTORIE
     * @param libelle  libellé français
     * @param demandes commandes annulées pour ce motif
     */
    @Schema(name = "MotifAnnulation")
    public record Motif(String code, String libelle, long demandes) {
    }
}
