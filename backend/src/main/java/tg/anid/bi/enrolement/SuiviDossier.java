package tg.anid.bi.enrolement;

import io.swagger.v3.oas.annotations.media.Schema;
import java.time.OffsetDateTime;

/**
 * Suivi d'un dossier (I11) : où en est une inscription, retrouvée par l'empreinte de son RID dans bi.suivi_dossier.
 * Le RID n'est jamais renvoyé : ni ici, ni dans un message d'erreur, ni dans un journal.
 *
 * @param typeDemande          type de demande MOSIP (NEW, UPDATE, LOST…)
 * @param devenir              niu, en_cours, echoue, rejete, non_classe ou non_recu (synchronisé, pas encore reçu)
 * @param bloque               vrai pour un dossier en cours dont la dernière transaction date de plus de 30 jours
 * @param centre               centre d'enrôlement, avec sa préfecture et sa région
 * @param etape                dernière étape du traitement, null tant que MOSIP n'a pas reçu le paquet
 * @param motif                motif donné par MOSIP (catalogue des motifs), null pour un dossier sans motif (NIU
 *                             généré, pas encore reçu) ; jamais le texte de MOSIP du dossier, seulement son message type
 * @param derniereActiviteLe   heure de la dernière transaction MOSIP, null si inconnue
 * @param jalons               dates de l'enrôlement au NIU
 * @param majLe                heure du calcul de ces informations (passage du pipeline)
 */
public record SuiviDossier(String typeDemande, String devenir, boolean bloque, Centre centre, Etape etape,
                           Motif motif, OffsetDateTime derniereActiviteLe, Jalons jalons, OffsetDateTime majLe) {

    /**
     * @param nom        nom du centre
     * @param prefecture préfecture, null si le centre n'est rattaché à aucune
     * @param region     région, null pour un centre hors référentiel
     */
    public record Centre(String nom, String prefecture, String region) {
    }

    /**
     * @param code    code MOSIP de l'étape (VALIDATE_PACKET…, REFUS_POSTE)
     * @param libelle libellé français
     * @param statut  statut MOSIP de la dernière transaction (SUCCESS, FAILED…), null si inconnu
     */
    @Schema(name = "EtapeSuivi")
    public record Etape(String code, String libelle, String statut) {
    }

    /**
     * @param code        code du motif (REFUS_SUPERVISEUR…)
     * @param libelle     motif en français (le code tant que le catalogue n'est pas publié)
     * @param commentaire message type de MOSIP pour ce motif (en anglais), null si aucun
     */
    @Schema(name = "MotifSuivi")
    public record Motif(String code, String libelle, String commentaire) {
    }

    /**
     * @param enroleLe      création du paquet au poste (horodatage contenu dans le RID)
     * @param synchroniseLe première synchronisation du poste avec MOSIP
     * @param refusPoste    vrai si une synchronisation a été refusée au poste
     * @param recuLe        réception du paquet par MOSIP
     * @param niuLe         génération du NIU
     */
    public record Jalons(OffsetDateTime enroleLe, OffsetDateTime synchroniseLe, boolean refusPoste,
                         OffsetDateTime recuLe, OffsetDateTime niuLe) {
    }
}
