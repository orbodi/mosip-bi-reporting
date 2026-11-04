package tg.anid.bi.authentifications;

import java.time.LocalDate;

/**
 * Bloc « Vérifications biométriques du traitement des paquets » : authentifications faites par MOSIP lui-même
 * (mosip-regproc-client) pendant le traitement des inscriptions. Jamais additionnées aux requêtes des usagers (option
 * A, 03/11/2026). Causes : GET /api/v1/authentifications/causes?perimetre=paquets. Contrôle : reussies + echouees +
 * autresStatuts = verifications. Chiffres à null tant que la source n'est pas alimentée.
 *
 * @param du            première date incluse, ou null
 * @param au            dernière date incluse, ou null
 * @param disponible    faux tant que le pipeline n'a publié aucune authentification
 * @param verifications vérifications biométriques sur la période
 * @param reussies      dont réussies
 * @param echouees      dont échouées
 * @param autresStatuts dont statut MOSIP inconnu (0 attendu)
 */
public record VerificationsPaquets(LocalDate du, LocalDate au, boolean disponible, Long verifications,
                                   Long reussies, Long echouees, Long autresStatuts) {
}
