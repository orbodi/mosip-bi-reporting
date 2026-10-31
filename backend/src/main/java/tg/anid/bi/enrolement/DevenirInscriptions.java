package tg.anid.bi.enrolement;

import java.time.LocalDate;

/**
 * Bloc « Devenir des inscriptions » de la page Enrôlement (docs/indicateurs.md : E-INS, E-NIU, E-COURS, E-ECH,
 * E-REJ). Contrôle : niuGeneres + enCours + echouees + rejetees + nonClassees = inscriptions ; enReprocessing ≤ enCours,
 * demandesMiseAJour + demandesNiuPerdu ≤ inscriptions (parties des totaux, pas des statuts de plus).
 *
 * @param perimetre    « Ensemble du Togo » ou nom de la zone filtrée
 * @param du           première date incluse (jour de réception), ou null depuis le début
 * @param au           dernière date incluse, ou null jusqu'à la dernière donnée
 * @param inscriptions paquets d'inscription reçus
 * @param niuGeneres   inscriptions abouties (statut regroupé « abouti »)
 * @param enCours      inscriptions ni abouties, ni échouées, ni rejetées
 * @param echouees     traitement en échec technique
 * @param rejetees     inscriptions rejetées
 * @param nonClassees  statut MOSIP sans correspondance validée (doit rester à 0 une fois la règle validée)
 * @param bloques      dont en cours depuis plus de 30 jours (stock à l'heure du dernier calcul) ; null quand une
 *                     période est demandée, le stock n'étant pas daté
 * @param enReprocessing    dont en cours dont la dernière transaction MOSIP est REPROCESS (MOSIP les reprendra) ;
 *                          suit la période comme enCours
 * @param demandesMiseAJour dont inscriptions de type mise à jour (UPDATE et RES_UPDATE)
 * @param demandesNiuPerdu  dont inscriptions de type NIU perdu (LOST)
 */
public record DevenirInscriptions(String perimetre, LocalDate du, LocalDate au, long inscriptions, long niuGeneres,
                                  long enCours, long echouees, long rejetees, long nonClassees, Long bloques,
                                  long enReprocessing, long demandesMiseAJour, long demandesNiuPerdu) {
}
