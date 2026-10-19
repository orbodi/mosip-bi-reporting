package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « Inscriptions et NIU par semaine » de la page Enrôlement : les 12 semaines complètes (lundi à dimanche)
 * qui finissent au plus tard à la fin de la période. Inscriptions comptées au jour de réception, NIU au jour de
 * génération (lecture flux, bi.fait_niu_jour) : la courbe des NIU suit le rythme réel de production.
 *
 * @param perimetre      « Ensemble du Togo » ou nom de la zone
 * @param du             première date demandée, ou null depuis le début
 * @param au             dernière date demandée, ou null jusqu'à la dernière donnée
 * @param niuDisponibles faux tant que bi.fait_niu_jour n'est pas alimentée : les NIU valent alors 0 et ne doivent
 *                       pas être affichés comme des zéros
 * @param semaines       de la plus ancienne à la plus récente ; vide s'il n'y a encore aucune donnée
 */
public record InscriptionsParSemaine(String perimetre, LocalDate du, LocalDate au, boolean niuDisponibles,
                                     List<Semaine> semaines) {

    /**
     * Une semaine complète.
     *
     * @param lundi          premier jour de la semaine
     * @param dansLaPeriode  vrai si la semaine touche la période demandée (sinon affichée en clair)
     * @param inscriptions   inscriptions reçues du lundi au dimanche
     * @param niuGeneres     NIU générés du lundi au dimanche
     */
    public record Semaine(LocalDate lundi, boolean dansLaPeriode, long inscriptions, long niuGeneres) {
    }
}
