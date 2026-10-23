package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « Territoire » de la page Enrôlement : totaux de la zone et une ligne par sous-zone directe (les régions pour
 * l'ensemble du Togo, les préfectures pour une région). Contrôle : la somme des lignes égale les totaux de la zone,
 * et les totaux égalent ceux du bloc « Devenir des inscriptions » sur la même zone et la même période.
 *
 * @param perimetre    « Ensemble du Togo » ou nom de la zone
 * @param zone         code de la zone, ou null pour l'ensemble du Togo
 * @param du           première date incluse (jour de réception), ou null depuis le début
 * @param au           dernière date incluse, ou null jusqu'à la dernière donnée
 * @param inscriptions inscriptions de la zone
 * @param niuGeneres   inscriptions abouties
 * @param enCours      inscriptions en cours
 * @param echouees     inscriptions en échec technique
 * @param rejetees     inscriptions rejetées
 * @param nonClassees  statut MOSIP sans correspondance validée
 * @param preinscriptions pré-inscriptions dont la préfecture de résidence déclarée est dans la zone (jour de création)
 * @param lignes       sous-zones dans l'ordre du référentiel (du nord au sud)
 */
public record Territoire(String perimetre, String zone, LocalDate du, LocalDate au, long inscriptions,
                         long niuGeneres, long enCours, long echouees, long rejetees, long nonClassees,
                         long preinscriptions, List<LigneZone> lignes) {

    /**
     * Une sous-zone et ses chiffres sur la période.
     *
     * @param code            code de la zone (bi.zone)
     * @param nom             nom affiché
     * @param niveau          region, prefecture, commune, canton, localite ou centre
     * @param horsReferentiel vrai pour la zone qui regroupe les centres absents du référentiel (affichée seulement si
     *                        elle a des inscriptions ou des pré-inscriptions)
     * @param preinscriptions pré-inscriptions dont la préfecture de résidence déclarée est dans la sous-zone
     */
    public record LigneZone(String code, String nom, String niveau, boolean horsReferentiel, long inscriptions,
                            long niuGeneres, long enCours, long echouees, long rejetees, long nonClassees,
                            long preinscriptions) {
    }
}
