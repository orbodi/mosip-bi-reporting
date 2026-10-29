package tg.anid.bi.enrolement;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « NIU générés par âge, sexe et nationalité » de la page Enrôlement (docs/indicateurs.md : E-NIU-PROFIL). Source :
 * enrichissement des NIU par l'ID Repository de MOSIP (pipeline mosip-cdc, lot 6), au jour de génération du NIU, région
 * du centre. Huit tranches de la maquette, de la plus jeune à la plus âgée ; une valeur nulle veut dire « non
 * disponible ». Contrôle : femmes + hommes des huit tranches + nonRenseignes = somme des nationalités = NIU générés de
 * la période (bi.fait_niu_jour).
 *
 * @param perimetre     « Ensemble du Togo » ou nom de la région filtrée
 * @param du            première date incluse (jour de génération), ou null depuis le début
 * @param au            dernière date incluse, ou null jusqu'à la dernière donnée
 * @param disponible    vrai dès que le pipeline a alimenté la source
 * @param tranches      les huit tranches, toujours présentes et dans l'ordre
 * @param nonRenseignes NIU dont le sexe ou l'âge manque (pas encore enrichi, genre inconnu, année absente)
 * @param nationalites  les cinq nationalités les plus nombreuses, puis « Autres » et « Non renseignée » s'il y en a
 */
public record AgeSexe(String perimetre, LocalDate du, LocalDate au, boolean disponible, List<Tranche> tranches,
                      Long nonRenseignes, List<Nationalite> nationalites) {

    /**
     * @param tranche code de la tranche : 0-5, 6-14, 15-18, 19-25, 26-35, 36-45, 46-60, 60+ (61 ans et plus)
     * @param femmes  NIU générés pour des femmes
     * @param hommes  NIU générés pour des hommes
     */
    public record Tranche(String tranche, Long femmes, Long hommes) {
    }

    /**
     * @param nom         libellé MOSIP de la nationalité, « Autres » ou « Non renseignée »
     * @param niuGeneres  NIU générés
     */
    @Schema(name = "NationaliteNiu")
    public record Nationalite(String nom, long niuGeneres) {
    }
}
