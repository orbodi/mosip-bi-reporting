package tg.anid.bi.enrolement;

import java.time.LocalDate;

/**
 * Bloc « Délais de traitement » de la page Enrôlement (I8, I9), en heures, depuis les histogrammes additifs de
 * bi.fait_delai_jour : exacts à l'heure près sous 48 h, au jour près au-delà (borne basse de la classe).
 *
 * @param perimetre           « Ensemble du Togo » ou nom de la zone
 * @param du                  première date incluse, ou null depuis le début
 * @param au                  dernière date incluse, ou null jusqu'à la dernière donnée
 * @param receptionNiu        de la réception par MOSIP au NIU : premières inscriptions (NEW), au jour du NIU
 * @param enrolementReception de l'enrôlement au poste à la réception par MOSIP : tous les paquets, au jour de réception
 */
public record DelaisTraitement(String perimetre, LocalDate du, LocalDate au, Mesure receptionNiu,
                               Mesure enrolementReception) {

    /**
     * Un délai mesuré.
     *
     * @param paquets    paquets mesurés
     * @param medianeH   médiane en heures, null sans paquet
     * @param centile90H 90e centile en heures, null sans paquet
     * @param moins24h   paquets dont le délai est inférieur à 24 h
     */
    public record Mesure(long paquets, Integer medianeH, Integer centile90H, long moins24h) {
    }
}
