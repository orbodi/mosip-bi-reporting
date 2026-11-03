package tg.anid.bi.cartes;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « Depuis quand ces cartes attendent » : cartes à remettre, par temps écoulé depuis leur expédition jusqu'au
 * jour du calcul (heure du Togo). Les cartes expédiées sur la période seulement, si une période est demandée.
 * Contrôle : somme des tranches = aRemettre = cartes à remettre du bloc « Impression et remise ».
 *
 * @param perimetre « Ensemble du Togo » ou nom de la zone
 * @param du        première date incluse (jour d'expédition), ou null
 * @param au        dernière date incluse, ou null
 * @param calculeLe jour du calcul de l'ancienneté
 * @param aRemettre cartes à remettre
 * @param tranches  moins_30j, 30_90j, 90_180j, plus_180j, dans cet ordre
 */
public record CartesEnAttente(String perimetre, LocalDate du, LocalDate au, LocalDate calculeLe, long aRemettre,
                              List<Tranche> tranches) {

    /**
     * Une tranche d'ancienneté.
     *
     * @param code        moins_30j, 30_90j, 90_180j ou plus_180j
     * @param depuisJours borne basse incluse, en jours depuis l'expédition
     * @param avantJours  borne haute exclue, ou null pour la dernière tranche
     * @param cartes      cartes à remettre de la tranche
     */
    @Schema(name = "TrancheAttente")
    public record Tranche(String code, int depuisJours, Integer avantJours, long cartes) {
    }
}
