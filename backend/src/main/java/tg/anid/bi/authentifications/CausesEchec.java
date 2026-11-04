package tg.anid.bi.authentifications;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « Causes des échecs » (A-CAUSE) d'un périmètre : usagers, ou traitement des paquets (bloc du bas). Motifs tirés
 * du message d'IDA par le pipeline (le message lui-même n'est jamais publié). Contrôle : somme des motifs = echecs =
 * échouées du périmètre.
 *
 * @param perimetre usagers ou paquets
 * @param du        première date incluse, ou null
 * @param au        dernière date incluse, ou null
 * @param echecs    authentifications échouées
 * @param motifs    du plus fréquent au moins fréquent (à égalité, par libellé)
 */
public record CausesEchec(String perimetre, LocalDate du, LocalDate au, long echecs, List<Motif> motifs) {

    /**
     * Un motif.
     *
     * @param code    code du pipeline (BIO_NON_CONCORDANTE…) ou AUTRE (non répertorié)
     * @param libelle libellé français
     * @param echecs  authentifications échouées pour ce motif
     */
    @Schema(name = "MotifEchecAuthentification")
    public record Motif(String code, String libelle, long echecs) {
    }
}
