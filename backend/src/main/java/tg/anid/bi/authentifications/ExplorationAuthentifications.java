package tg.anid.bi.authentifications;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

/**
 * Onglet Authentifications de l'Exploration : requêtes, réussies et échouées d'un périmètre (usagers ou traitement des
 * paquets, jamais additionnés), filtrées par type, motif d'échec et appelant, ventilées par année, mois, type, motif
 * ou appelant. Contrôles : reussies + echouees ≤ requetes (le reste : statut inconnu) ; somme des lignes = total
 * (sauf ventilation par motif : seulement les échouées). Les listes de valeurs alimentent les filtres de l'onglet.
 *
 * @param perimetre usagers ou paquets
 * @param du        première date incluse, ou null
 * @param au        dernière date incluse, ou null
 * @param par       annee, mois, type, motif, appelant ou total
 * @param lignes    une ligne par valeur de la ventilation (vide pour total), dans l'ordre de la ventilation
 * @param total     totaux de la sélection
 * @param valeurs   valeurs possibles des filtres du périmètre, sur toute la durée
 */
public record ExplorationAuthentifications(String perimetre, LocalDate du, LocalDate au, String par,
                                           List<Ligne> lignes, Chiffres total, Valeurs valeurs) {

    /**
     * Requêtes, réussies et échouées.
     *
     * @param requetes authentifications
     * @param reussies dont réussies
     * @param echouees dont échouées
     */
    @Schema(name = "ChiffresExplorationAuthentification")
    public record Chiffres(long requetes, long reussies, long echouees) {
    }

    /**
     * Une ligne de la ventilation.
     *
     * @param cle      année (aaaa), mois (aaaa-mm), code du type ou du motif, ou nom de l'appelant
     * @param libelle  libellé du motif ; sinon la clé (le front met en forme les mois et les types)
     * @param chiffres chiffres de la ligne
     */
    @Schema(name = "LigneExplorationAuthentification")
    public record Ligne(String cle, String libelle, Chiffres chiffres) {
    }

    /**
     * Valeurs possibles des filtres.
     *
     * @param types     codes des types présents (biometrique, otp…)
     * @param motifs    motifs d'échec présents, avec leur libellé
     * @param appelants noms des appelants (partenaires et services de l'ANID), sans code MOSIP
     */
    @Schema(name = "ValeursExplorationAuthentification")
    public record Valeurs(List<String> types, List<CausesEchec.Motif> motifs, List<String> appelants) {
    }
}
