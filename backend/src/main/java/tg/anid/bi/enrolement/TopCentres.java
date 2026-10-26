package tg.anid.bi.enrolement;

import java.util.List;

/**
 * Bloc « Top des centres » de la page Enrôlement : les cinq centres de la zone qui ont le plus d'inscriptions,
 * d'échecs ou de rejets sur la période, ou la remontée la plus lente (paquets synchronisés non reçus depuis plus de
 * 7 jours, à l'heure du dernier calcul). Un centre sans valeur n'entre pas dans le classement.
 *
 * @param perimetre  « Ensemble du Togo » ou nom de la zone
 * @param classement inscriptions, echecs, rejets ou remontee
 * @param centres    du premier au cinquième au plus
 */
public record TopCentres(String perimetre, String classement, List<CentreClasse> centres) {

    /**
     * Un centre classé.
     *
     * @param rang         1 pour le premier
     * @param code         code du centre (bi.zone)
     * @param nom          nom du centre
     * @param prefecture   nom de sa préfecture, ou null si le centre n'est rattaché à aucune
     * @param region       nom de sa région
     * @param valeur       inscriptions, échecs, rejets ou paquets en retard selon le classement
     * @param inscriptions inscriptions du centre sur la période (dénominateur d'un taux éventuel)
     */
    public record CentreClasse(int rang, String code, String nom, String prefecture, String region, long valeur,
                               long inscriptions) {
    }
}
