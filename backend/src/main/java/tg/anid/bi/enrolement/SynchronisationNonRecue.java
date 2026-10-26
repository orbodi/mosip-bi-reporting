package tg.anid.bi.enrolement;

import java.time.OffsetDateTime;

/**
 * Paquets synchronisés par le poste mais pas encore reçus par MOSIP (I10), à l'heure du dernier calcul. Moins de
 * 7 jours : en transit probable ; plus de 7 jours : à rechercher au poste.
 *
 * @param perimetre      « Ensemble du Togo » ou nom de la zone
 * @param calculeLe      heure du calcul (passage dbt), null tant que rien n'est publié
 * @param nonRecus       paquets synchronisés non reçus
 * @param plusDe7Jours   dont synchronisés il y a plus de 7 jours
 * @param plusAncienneLe synchronisation la plus ancienne encore non reçue, null sans paquet
 */
public record SynchronisationNonRecue(String perimetre, OffsetDateTime calculeLe, long nonRecus, long plusDe7Jours,
                                      OffsetDateTime plusAncienneLe) {
}
