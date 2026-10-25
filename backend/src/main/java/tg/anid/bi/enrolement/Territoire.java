package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « Territoire » de la page Enrôlement : totaux de la zone et une ligne par sous-zone directe, à tout niveau de
 * l'arborescence bi.zone (région → préfecture → commune → canton → localité → centre). Contrôle : la somme des lignes
 * égale les totaux de la zone, et les totaux égalent ceux du bloc « Devenir des inscriptions » sur la même zone et la
 * même période.
 *
 * @param perimetre    « Ensemble du Togo » ou nom de la zone
 * @param zone         code de la zone, ou null pour l'ensemble du Togo
 * @param niveau       niveau de la zone (region, prefecture, commune, canton, localite, centre), null pour le Togo
 * @param ascendants   zones au-dessus de la zone, de la région à son parent direct (fil d'Ariane) ; vide pour le Togo
 *                     et pour une région
 * @param du           première date incluse (jour de réception), ou null depuis le début
 * @param au           dernière date incluse, ou null jusqu'à la dernière donnée
 * @param inscriptions inscriptions de la zone
 * @param niuGeneres   inscriptions abouties
 * @param enCours      inscriptions en cours
 * @param echouees     inscriptions en échec technique
 * @param rejetees     inscriptions rejetées
 * @param nonClassees  statut MOSIP sans correspondance validée
 * @param preinscriptions pré-inscriptions dont la préfecture de résidence déclarée est dans la zone (jour de création)
 * @param delaiMedianH délai médian de la réception au NIU, en heures (nouvelles inscriptions, NIU générés sur la
 *                     période) ; null sans NIU
 * @param lignes       sous-zones dans l'ordre du référentiel (du nord au sud)
 */
public record Territoire(String perimetre, String zone, String niveau, List<ZoneParente> ascendants, LocalDate du,
                         LocalDate au, long inscriptions,
                         long niuGeneres, long enCours, long echouees, long rejetees, long nonClassees,
                         long preinscriptions, Integer delaiMedianH, List<LigneZone> lignes) {

    /**
     * Une sous-zone et ses chiffres sur la période.
     *
     * @param code            code de la zone (bi.zone)
     * @param nom             nom affiché
     * @param niveau          region, prefecture, commune, canton, localite ou centre
     * @param horsReferentiel vrai pour la zone qui regroupe les centres absents du référentiel (affichée seulement si
     *                        elle a des inscriptions ou des pré-inscriptions)
     * @param preinscriptions pré-inscriptions dont la préfecture de résidence déclarée est dans la sous-zone
     * @param delaiMedianH    délai médian de la réception au NIU dans la sous-zone, en heures ; null sans NIU
     * @param ouvrable        vrai si la sous-zone a elle-même des sous-zones (on peut y descendre)
     */
    public record LigneZone(String code, String nom, String niveau, boolean horsReferentiel, long inscriptions,
                            long niuGeneres, long enCours, long echouees, long rejetees, long nonClassees,
                            long preinscriptions, Integer delaiMedianH, boolean ouvrable) {

        /** La même ligne, avec son délai médian. */
        public LigneZone avecDelai(Integer delai) {
            return new LigneZone(code, nom, niveau, horsReferentiel, inscriptions, niuGeneres, enCours, echouees,
                    rejetees, nonClassees, preinscriptions, delai, ouvrable);
        }
    }

    /**
     * Une zone au-dessus de la zone affichée.
     *
     * @param code   code bi.zone
     * @param nom    nom affiché
     * @param niveau region, prefecture, commune, canton ou localite
     */
    public record ZoneParente(String code, String nom, String niveau) {
    }
}
