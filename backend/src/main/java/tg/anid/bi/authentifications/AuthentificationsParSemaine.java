package tg.anid.bi.authentifications;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « Requêtes par semaine » : requêtes réussies et échouées des usagers des 12 semaines complètes (lundi à
 * dimanche) qui finissent au plus tard à la fin de la période, ou à la dernière donnée d'authentification.
 *
 * @param du       première date de la période, ou null
 * @param au       dernière date de la période, ou null
 * @param semaines de la plus ancienne à la plus récente ; vide tant que la source n'est pas alimentée
 */
public record AuthentificationsParSemaine(LocalDate du, LocalDate au, List<Semaine> semaines) {

    /**
     * Une semaine.
     *
     * @param lundi       premier jour de la semaine
     * @param dansPeriode vrai si la semaine a au moins un jour dans la période
     * @param reussies    requêtes réussies
     * @param echouees    requêtes échouées
     */
    @Schema(name = "SemaineAuthentification")
    public record Semaine(LocalDate lundi, boolean dansPeriode, long reussies, long echouees) {
    }
}
