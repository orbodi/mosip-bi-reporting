package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.time.OffsetDateTime;

/**
 * Bloc « Pré-inscription » de la page Enrôlement (docs/indicateurs.md : E-PRE, E-PRE-RDV, E-PRE-ATT, E-PRE-EXP,
 * E-PRE-HON). Source : prereg.applicant_demographic et _consumed, colonnes sans identité (décision du 20/10/2026).
 * Contrôle : rendezVousReserves + enAttenteRendezVous + expirees + annulees + nonClassees = demandes.
 * Une valeur nulle veut dire « non disponible », jamais zéro : source pas encore alimentée, utilisateur régional (une
 * pré-inscription n'a pas de territoire), ou sexe sans source anonymisée.
 *
 * @param perimetre           « Ensemble du Togo », ou la zone d'un utilisateur régional
 * @param du                  première date incluse (jour de création de la demande), ou null depuis le début
 * @param au                  dernière date incluse, ou null jusqu'à la dernière donnée
 * @param disponible          vrai dès que le pipeline a alimenté la source
 * @param demandes            demandes de pré-enrôlement créées
 * @param rendezVousReserves  demandes au statut regroupé « réservée »
 * @param enAttenteRendezVous demandes au statut regroupé « en attente de rendez-vous »
 * @param expirees            demandes au statut regroupé « expirée »
 * @param annulees            demandes au statut regroupé « annulée »
 * @param honorees            demandes reprises lors d'une inscription en centre (table _consumed)
 * @param nonClassees         statut MOSIP sans correspondance validée
 * @param femmes              toujours null : pas de source anonymisée du sexe pour les pré-inscriptions
 * @param hommes              toujours null, comme {@code femmes}
 * @param derniereDemande     création de la demande la plus récente (bi.source_fraicheur, source « preinscription »)
 */
public record Preinscriptions(String perimetre, LocalDate du, LocalDate au, boolean disponible, Long demandes,
                              Long rendezVousReserves, Long enAttenteRendezVous, Long expirees, Long annulees,
                              Long honorees, Long nonClassees, Long femmes, Long hommes,
                              OffsetDateTime derniereDemande) {

    /** Bloc sans chiffres : source pas encore alimentée, ou hors de la portée de l'utilisateur. */
    static Preinscriptions nonDisponible(String perimetre, LocalDate du, LocalDate au) {
        return new Preinscriptions(perimetre, du, au, false, null, null, null, null, null, null, null, null, null,
                null);
    }
}
