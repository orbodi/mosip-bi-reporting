package tg.anid.bi.cartes;

import java.time.LocalDate;

/**
 * Bloc « Impression et remise » de la page Impression des cartes (docs/indicateurs.md : I-DEM, I-ATT, I-REJ, I-ANN,
 * I-EXP, I-REM, I-AREM, I-DELAI). Deux lectures « cohorte » : les commandes au jour de leur réception, dans leur statut
 * d'aujourd'hui ; les cartes au jour de leur expédition, remises ou non aujourd'hui. Contrôles : envoyees + enAttente +
 * rejetees + nonClassees = demandes ; annulees ≤ demandes (comptées à part) ; remises + aRemettre = expediees ;
 * remisesHorsLigne + remisesEnLigne + remisesSupport + remisesAutre = remises. Les chiffres valent null tant que la
 * source n'est pas alimentée ({@code disponible} faux).
 *
 * @param perimetre         « Ensemble du Togo » ou nom de la zone filtrée
 * @param du                première date incluse, ou null depuis le début
 * @param au                dernière date incluse, ou null jusqu'à la dernière donnée
 * @param disponible        faux tant que le pipeline n'a publié aucune commande
 * @param demandes          commandes d'impression reçues sur la période (I-DEM)
 * @param envoyees          dont envoyées à l'imprimeur (prc_status OK)
 * @param enAttente         dont pas encore envoyées (NEW, I-ATT)
 * @param rejetees          dont rejetées (KO, I-REJ)
 * @param nonClassees       dont statut MOSIP sans correspondance (0 attendu)
 * @param annulees          dont annulées, comptées à part : elles restent aussi dans leur statut (I-ANN)
 * @param derniereRejetee   jour de réception de la plus récente commande rejetée de la période, ou null
 * @param expediees         cartes expédiées sur la période (I-EXP)
 * @param remises           dont remises au citoyen (I-REM)
 * @param remisesHorsLigne  remises hors ligne (OFFLINE)
 * @param remisesEnLigne    remises en ligne (ONLINE)
 * @param remisesSupport    remises par le support (SUPPORT)
 * @param remisesAutre      remises au mode absent ou inconnu (0 attendu)
 * @param aRemettre         dont pas encore remises (I-AREM)
 * @param delaiMedianJours  médiane du délai du NIU à la remise, en jours, sur les cartes remises (I-DELAI) ; null
 *                          sans carte remise
 * @param erreursIdps       dont commandes avec au moins une erreur d'envoi à l'IDPS (I-ERR), même renvoyées ensuite
 * @param derniereErreurIdps jour de réception de la plus récente commande en erreur de la période, ou null
 * @param niuSansCommande   NIU de première inscription sans commande d'impression (I-SANS), stock à l'heure du
 *                          dernier calcul ; null quand une période est demandée (stock non daté)
 * @param niuSansCommandePlus7j dont NIU générés depuis plus de 7 jours ; null quand une période est demandée
 */
public record ImpressionRemise(String perimetre, LocalDate du, LocalDate au, boolean disponible, Long demandes,
                               Long envoyees, Long enAttente, Long rejetees, Long nonClassees, Long annulees,
                               LocalDate derniereRejetee, Long expediees, Long remises, Long remisesHorsLigne,
                               Long remisesEnLigne, Long remisesSupport, Long remisesAutre, Long aRemettre,
                               Integer delaiMedianJours, Long erreursIdps, LocalDate derniereErreurIdps,
                               Long niuSansCommande, Long niuSansCommandePlus7j) {

    /** Bloc sans chiffres, tant que la source n'est pas alimentée. */
    static ImpressionRemise nonDisponible(String perimetre, LocalDate du, LocalDate au) {
        return new ImpressionRemise(perimetre, du, au, false, null, null, null, null, null, null, null, null, null,
                null, null, null, null, null, null, null, null, null, null);
    }
}
