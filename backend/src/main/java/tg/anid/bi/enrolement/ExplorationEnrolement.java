package tg.anid.bi.enrolement;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

/**
 * Onglet Enrôlement de l'Exploration (lots E1 et E2, 06 et 07/11/2026) : inscriptions et leur devenir (jour de
 * réception, devenir d'aujourd'hui) et pré-inscriptions (jour de création, préfecture de résidence déclarée), pour une
 * zone de tout niveau (tout le Togo par défaut), filtrées par type de demande MOSIP, sexe, tranche d'âge et
 * nationalité, ventilées par sous-zone directe, année, mois, type, sexe, tranche d'âge ou nationalité. Le profil (sexe,
 * âge, nationalité) ne vient que de l'ID Repository : seules les inscriptions devenues NIU et enrichies en ont un, les
 * autres sont en « I », « inconnu », « Non renseignée ». Contrôles : niuGeneres + enCours + echouees + rejetees ≤
 * inscriptions (le reste est non classé) ; somme des lignes = total.
 *
 * @param perimetre « Ensemble du Togo » ou nom de la zone
 * @param zone      code de la zone, ou null pour l'ensemble du Togo
 * @param du        première date incluse, ou null
 * @param au        dernière date incluse, ou null
 * @param type      type de demande MOSIP filtré (NEW, UPDATE, LOST…), ou null pour tous
 * @param par          sous, annee, mois, type, sexe, age, nationalite ou total
 * @param lignes       une ligne par valeur de la ventilation (vide pour total)
 * @param total        totaux de la zone sur la période
 * @param types        types de demande présents dans les données (codes MOSIP), seulement pour {@code par} total ;
 *                     sinon vide
 * @param nationalites nationalités présentes dans les données, de la plus fréquente à la moins fréquente, seulement
 *                     pour {@code par} total ; sinon vide
 */
public record ExplorationEnrolement(String perimetre, String zone, LocalDate du, LocalDate au, String type,
                                    String par, List<Ligne> lignes, Chiffres total, List<String> types,
                                    List<String> nationalites) {

    /**
     * Les indicateurs de l'onglet.
     *
     * @param preinscriptions pré-inscriptions ; null quand un type de demande ou un profil est filtré ou ventilé (une
     *                        pré-inscription n'a ni type de demande, ni profil par centre)
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
     * @param cle             code de la sous-zone, année (aaaa), mois (aaaa-mm), type de demande MOSIP, sexe (F, H, I),
     *                        tranche d'âge (0-5 … 60+, inconnu) ou nationalité
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
