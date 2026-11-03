package tg.anid.bi.cartes;

import io.swagger.v3.oas.annotations.media.Schema;

import java.util.List;

/**
 * Bloc « Top des centres » de la page Impression des cartes : les cinq centres de la zone qui ont remis le plus de
 * cartes, parmi les cartes expédiées sur la période. Un centre sans remise n'est pas classé ; à égalité, ordre
 * alphabétique.
 *
 * @param perimetre « Ensemble du Togo » ou nom de la zone
 * @param centres   du premier au cinquième au plus
 */
public record TopCentresCartes(String perimetre, List<CentreClasse> centres) {

    /**
     * Un centre classé.
     *
     * @param rang       1 pour le premier
     * @param code       code du centre (bi.zone)
     * @param nom        nom du centre
     * @param prefecture nom de sa préfecture, ou null
     * @param region     nom de sa région
     * @param remises    cartes remises
     * @param expediees  cartes expédiées du centre (dénominateur du pourcentage)
     */
    @Schema(name = "CentreCartes")
    public record CentreClasse(int rang, String code, String nom, String prefecture, String region, long remises,
                               long expediees) {
    }
}
