package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « NIU générés par âge et par sexe » de la page Enrôlement (docs/indicateurs.md : E-NIU-PROFIL). Source :
 * idrepo.anonymous_profile (MOSIP 1.1.5.5 et plus), profils « New », au jour de génération du NIU.
 * Huit tranches de la maquette, de la plus jeune à la plus âgée ; une valeur nulle veut dire « non disponible ».
 *
 * @param perimetre     « Ensemble du Togo » ou nom de la région filtrée
 * @param du            première date incluse (jour de génération), ou null depuis le début
 * @param au            dernière date incluse, ou null jusqu'à la dernière donnée
 * @param disponible    vrai dès que le pipeline a alimenté la source
 * @param tranches      les huit tranches, toujours présentes et dans l'ordre
 * @param nonRenseignes NIU dont le sexe ou l'âge manque (genre sans correspondance validée, année absente)
 */
public record AgeSexe(String perimetre, LocalDate du, LocalDate au, boolean disponible, List<Tranche> tranches,
                      Long nonRenseignes) {

    /**
     * @param tranche code de la tranche : 0-5, 6-14, 15-18, 19-25, 26-35, 36-45, 46-60, 60+ (61 ans et plus)
     * @param femmes  NIU générés pour des femmes
     * @param hommes  NIU générés pour des hommes
     */
    public record Tranche(String tranche, Long femmes, Long hommes) {
    }
}
