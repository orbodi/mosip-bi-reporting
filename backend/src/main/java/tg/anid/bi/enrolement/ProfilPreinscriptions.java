package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « Profil des pré-inscrits » de la page Enrôlement : demandes par tranche d'âge et sexe (pyramide) et par
 * nationalité. Source : champs extraits de l'API de pré-inscription MOSIP (pipeline mosip-cdc). Nationale, comme le
 * bloc « Pré-inscription ».
 * Contrôle : femmes + hommes des neuf tranches + nonRenseignes = somme des nationalités = demandes de la période ;
 * femmes et hommes des neuf tranches = femmes et hommes du bloc « Pré-inscription ».
 *
 * @param perimetre     « Ensemble du Togo »
 * @param du            première date incluse (jour de création de la demande), ou null depuis le début
 * @param au            dernière date incluse, ou null jusqu'à la dernière donnée
 * @param disponible    vrai dès que le pipeline a alimenté la source
 * @param tranches      les huit tranches d'âge puis « inconnu » (sexe connu, âge non renseigné), femmes et hommes
 *                      (null si non disponible)
 * @param nonRenseignes demandes sans sexe connu (demande pas encore enrichie, ou genre absent)
 * @param nationalites  les cinq nationalités les plus nombreuses, puis « Autres » et « Non renseignée » s'il y en a
 */
public record ProfilPreinscriptions(String perimetre, LocalDate du, LocalDate au, boolean disponible,
                                    List<AgeSexe.Tranche> tranches, Long nonRenseignes,
                                    List<Nationalite> nationalites) {

    /**
     * @param nom      libellé MOSIP de la nationalité, « Autres » ou « Non renseignée »
     * @param demandes demandes de pré-enrôlement
     */
    public record Nationalite(String nom, long demandes) {
    }

    /** Bloc sans chiffres : source pas encore alimentée. */
    static ProfilPreinscriptions nonDisponible(String perimetre, LocalDate du, LocalDate au, List<String> tranches) {
        List<AgeSexe.Tranche> vides = tranches.stream().map(t -> new AgeSexe.Tranche(t, null, null)).toList();
        return new ProfilPreinscriptions(perimetre, du, au, false, vides, null, List.of());
    }
}
