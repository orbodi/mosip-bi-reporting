package tg.anid.bi.enrolement;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

/**
 * Onglet Enrôlement de l'Exploration (lot E1, 06/11/2026) : inscriptions et leur devenir (jour de réception, devenir
 * d'aujourd'hui) et pré-inscriptions (jour de création, préfecture de résidence déclarée), pour une zone de tout niveau
 * (tout le Togo par défaut), filtrées par type de demande MOSIP, ventilées par sous-zone directe, par année, par mois
 * ou par type de demande. Contrôles : niuGeneres + enCours + echouees + rejetees ≤ inscriptions (le reste est non
 * classé) ; somme des lignes = total.
 *
 * @param perimetre « Ensemble du Togo » ou nom de la zone
 * @param zone      code de la zone, ou null pour l'ensemble du Togo
 * @param du        première date incluse, ou null
 * @param au        dernière date incluse, ou null
 * @param type      type de demande MOSIP filtré (NEW, UPDATE, LOST…), ou null pour tous
 * @param par       sous, annee, mois, type ou total
 * @param lignes    une ligne par valeur de la ventilation (vide pour total)
 * @param total     totaux de la zone sur la période
 * @param types     types de demande présents dans les données (codes MOSIP), seulement pour {@code par} total ; sinon
 *                  vide
 */
public record ExplorationEnrolement(String perimetre, String zone, LocalDate du, LocalDate au, String type,
                                    String par, List<Ligne> lignes, Chiffres total, List<String> types) {

    /**
     * Les indicateurs de l'onglet.
     *
     * @param preinscriptions pré-inscriptions ; null quand un type de demande est filtré ou ventilé (une
     *                        pré-inscription n'a pas de type de demande)
     */
    @Schema(name = "ChiffresExplorationEnrolement")
    public record Chiffres(long inscriptions, long niuGeneres, long enCours, long echouees, long rejetees,
                           Long preinscriptions) {

        Chiffres sansPreinscriptions() {
            return new Chiffres(inscriptions, niuGeneres, enCours, echouees, rejetees, null);
        }
    }

    /**
     * Une ligne de la ventilation.
     *
     * @param cle             code de la sous-zone, année (aaaa), mois (aaaa-mm) ou type de demande MOSIP
     * @param libelle         nom de la sous-zone ; sinon la clé (le front met en forme les mois et les types)
     * @param niveau          niveau de la sous-zone, null sinon
     * @param horsReferentiel vrai pour la zone des centres absents du référentiel
     * @param ouvrable        vrai si la sous-zone a elle-même des sous-zones
     */
    @Schema(name = "LigneExplorationEnrolement")
    public record Ligne(String cle, String libelle, String niveau, boolean horsReferentiel, boolean ouvrable,
                        Chiffres chiffres) {

        Ligne sansPreinscriptions() {
            return new Ligne(cle, libelle, niveau, horsReferentiel, ouvrable, chiffres.sansPreinscriptions());
        }
    }
}
