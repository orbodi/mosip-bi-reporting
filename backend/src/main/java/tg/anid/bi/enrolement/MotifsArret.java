package tg.anid.bi.enrolement;

import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;

/**
 * Bloc « Où s'arrêtent les paquets » par motif (décision du 26/10/2026, migration V9) : pour chaque devenir (rejetés,
 * échoués, en cours), les cas par étape de traitement (reg_stage_name de MOSIP) et motif (status_comment de MOSIP rangé
 * par le catalogue des motifs), du plus fréquent au moins fréquent ; les lignes de moins de 1 % du devenir sont
 * regroupées en « Autres cas » (motif null), en dernier. Le texte de MOSIP d'une inscription n'est jamais renvoyé :
 * seulement le message type du catalogue.
 * Contrôles : totalRejets = rejetees et totalEchecs = echouees du bloc « Devenir » (même zone, même période) ;
 * totalEnCours = enCours du bloc « Devenir » sans période.
 *
 * @param perimetre    « Ensemble du Togo » ou nom de la zone
 * @param du           première date incluse (jour de réception) des rejets et échecs, ou null depuis le début
 * @param au           dernière date incluse, ou null jusqu'à la dernière donnée
 * @param calculeLe    heure du calcul du stock des en cours, null tant que rien n'est publié
 * @param seuilJours   ancienneté au-delà de laquelle un paquet en cours est dit bloqué (30)
 * @param totalRejets  paquets rejetés
 * @param totalEchecs  paquets échoués
 * @param totalEnCours paquets en cours (stock, sans période)
 * @param bloques      dont bloqués
 * @param rejets       lignes des rejetés
 * @param echecs       lignes des échoués
 * @param enCours      lignes des en cours
 */
public record MotifsArret(String perimetre, LocalDate du, LocalDate au, OffsetDateTime calculeLe, int seuilJours,
                          long totalRejets, long totalEchecs, long totalEnCours, long bloques, List<Ligne> rejets,
                          List<Ligne> echecs, List<Ligne> enCours) {

    /**
     * Une étape et un motif.
     *
     * @param motif         code du motif (REFUS_SUPERVISEUR…), null pour « Autres cas »
     * @param libelle       motif en français
     * @param commentaire   message type de MOSIP pour ce motif (catalogue), null si aucun
     * @param piste         ce qu'il faut vérifier pour ce motif (catalogue), null pour « Autres cas »
     * @param stage         étape de traitement de MOSIP (PacketValidatorStage…), null pour « Autres cas »
     * @param stageLibelle  étape en français, null pour « Autres cas »
     * @param inscriptions  paquets
     * @param bloques       dont bloqués depuis plus de 30 jours (en cours seulement, 0 sinon)
     */
    @Schema(name = "LigneMotif")
    public record Ligne(String motif, String libelle, String commentaire, String piste, String stage,
                        String stageLibelle, long inscriptions, long bloques) {
    }
}
