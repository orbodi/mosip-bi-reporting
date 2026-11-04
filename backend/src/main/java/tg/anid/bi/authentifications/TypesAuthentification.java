package tg.anid.bi.authentifications;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « Par type d'authentification » (A-TYPE) : requêtes et échecs des usagers pour chaque famille de modalités,
 * dans un ordre fixe (biometrique, otp, demographique, combinee, sans_mode, non_classe), y compris à 0.
 * Contrôle : somme des requêtes = requetes du bloc des usagers.
 *
 * @param du    première date incluse, ou null
 * @param au    dernière date incluse, ou null
 * @param types une ligne par type
 */
public record TypesAuthentification(LocalDate du, LocalDate au, List<Type> types) {

    /**
     * Un type.
     *
     * @param code     biometrique, otp, demographique, combinee, sans_mode ou non_classe
     * @param requetes authentifications de ce type
     * @param echecs   dont échouées
     */
    @Schema(name = "TypeAuthentification")
    public record Type(String code, long requetes, long echecs) {
    }
}
