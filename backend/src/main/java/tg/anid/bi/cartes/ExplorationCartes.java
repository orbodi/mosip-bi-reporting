package tg.anid.bi.cartes;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

/**
 * Onglet Impression des cartes de l'Exploration : demandes d'impression (jour de réception de la commande), cartes
 * imprimées et expédiées, remises et à remettre (jour d'expédition, statut d'aujourd'hui), pour une zone de tout niveau
 * (tout le Togo par défaut), ventilées par sous-zone directe, par année ou par mois. Pas de profil (sexe, âge, type de
 * demande) : les faits d'impression n'en portent pas. Contrôles : remises + aRemettre = expediees sur chaque ligne ;
 * somme des lignes = total (y compris la ligne des centres hors référentiel quand elle a des chiffres).
 *
 * @param perimetre « Ensemble du Togo » ou nom de la zone
 * @param zone      code de la zone, ou null pour l'ensemble du Togo
 * @param du        première date incluse, ou null
 * @param au        dernière date incluse, ou null
 * @param par       sous, annee, mois ou total
 * @param lignes    une ligne par valeur de la ventilation (vide pour total) : sous-zones dans l'ordre du référentiel,
 *                  années et mois dans l'ordre du temps
 * @param total     totaux de la zone sur la période
 */
public record ExplorationCartes(String perimetre, String zone, LocalDate du, LocalDate au, String par,
                                List<Ligne> lignes, Chiffres total) {

    /**
     * Les quatre indicateurs de l'onglet.
     *
     * @param demandes  commandes d'impression reçues (I-DEM)
     * @param expediees cartes imprimées et expédiées (I-EXP)
     * @param remises   dont remises au citoyen (I-REM)
     * @param aRemettre dont pas encore remises (I-AREM)
     */
    @Schema(name = "ChiffresExplorationCartes")
    public record Chiffres(long demandes, long expediees, long remises, long aRemettre) {
    }

    /**
     * Une ligne de la ventilation.
     *
     * @param cle             code de la sous-zone, année (aaaa) ou mois (aaaa-mm)
     * @param libelle         nom de la sous-zone ; sinon la clé (le front met en forme les mois)
     * @param niveau          niveau de la sous-zone, null pour une année ou un mois
     * @param horsReferentiel vrai pour la zone des centres absents du référentiel
     * @param ouvrable        vrai si la sous-zone a elle-même des sous-zones
     * @param chiffres        chiffres de la ligne
     */
    @Schema(name = "LigneExplorationCartes")
    public record Ligne(String cle, String libelle, String niveau, boolean horsReferentiel, boolean ouvrable,
                        Chiffres chiffres) {
    }
}
