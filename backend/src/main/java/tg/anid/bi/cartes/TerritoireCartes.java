package tg.anid.bi.cartes;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

import tg.anid.bi.enrolement.Territoire;

/**
 * Bloc « Cartes à remettre par région » : cartes expédiées sur la période (jour d'expédition), remises et à remettre
 * aujourd'hui, pour la zone et chacune de ses sous-zones directes (lieu = centre d'enrôlement, qui est le lieu de
 * remise). Contrôles : remises + aRemettre = expediees, sur chaque ligne ; somme des lignes = totaux de la zone =
 * bloc « Impression et remise ».
 *
 * @param perimetre  « Ensemble du Togo » ou nom de la zone
 * @param zone       code de la zone, ou null pour l'ensemble du Togo
 * @param niveau     niveau de la zone, null pour le Togo
 * @param ascendants zones au-dessus de la zone, de la région à son parent direct ; vide pour le Togo et une région
 * @param du         première date incluse (jour d'expédition), ou null
 * @param au         dernière date incluse, ou null
 * @param expediees  cartes expédiées de la zone
 * @param remises    dont remises
 * @param aRemettre  dont à remettre
 * @param lignes     sous-zones dans l'ordre du référentiel (du nord au sud)
 */
public record TerritoireCartes(String perimetre, String zone, String niveau, List<Territoire.ZoneParente> ascendants,
                               LocalDate du, LocalDate au, long expediees, long remises, long aRemettre,
                               List<LigneZone> lignes) {

    /**
     * Une sous-zone.
     *
     * @param code            code bi.zone
     * @param nom             nom affiché
     * @param niveau          region, prefecture, commune, canton, localite ou centre
     * @param horsReferentiel vrai pour la zone des centres absents du référentiel (affichée seulement si elle a des
     *                        cartes)
     * @param ouvrable        vrai si la sous-zone a elle-même des sous-zones
     */
    @Schema(name = "LigneZoneCartes")
    public record LigneZone(String code, String nom, String niveau, boolean horsReferentiel, boolean ouvrable,
                            long expediees, long remises, long aRemettre) {
    }
}
