package tg.anid.bi.enrolement;

import java.time.LocalDate;

import jakarta.validation.constraints.Pattern;

import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/enrolement")
public class EnrolementController {

    private final EnrolementService service;
    private final EnrolementTraitementService traitement;

    public EnrolementController(EnrolementService service, EnrolementTraitementService traitement) {
        this.service = service;
        this.traitement = traitement;
    }

    /**
     * Devenir des inscriptions (page Enrôlement). Données mises à jour en continu par le pipeline temps réel :
     * le front relit ce bloc toutes les 30 secondes.
     */
    @GetMapping("/devenir")
    public DevenirInscriptions devenir(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return service.devenir(du, au, zone);
    }

    /**
     * Inscriptions (jour de réception) et NIU générés (jour de génération) des 12 semaines complètes qui finissent
     * au plus tard à la fin de la période.
     */
    @GetMapping("/semaines")
    public InscriptionsParSemaine semaines(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return service.semaines(du, au, zone);
    }

    /**
     * Inscriptions (jour de réception) et NIU générés (jour de génération) des 28 derniers jours, aujourd'hui compris
     * (heure du Togo). National, sans période : le bloc suit la date du jour.
     */
    @GetMapping("/jours")
    public InscriptionsParJour jours() {
        return service.jours();
    }

    /** Territoire : totaux de la zone (tout le Togo par défaut) et une ligne par sous-zone directe. */
    @GetMapping("/territoire")
    public Territoire territoire(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return service.territoire(du, au, zone);
    }

    /**
     * Pré-inscriptions (bloc national, sans paramètre de zone) : demandes, rendez-vous, en attente, expirées,
     * honorées et dernière demande. Les chiffres valent null quand la source n'est pas disponible.
     */
    @GetMapping("/preinscriptions")
    public Preinscriptions preinscriptions(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au) {
        return service.preinscriptions(du, au);
    }

    /** Profil des pré-inscrits : tranche d'âge et sexe, nationalité (national). */
    @GetMapping("/preinscriptions/profil")
    public ProfilPreinscriptions profilPreinscriptions(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au) {
        return service.profilPreinscriptions(du, au);
    }

    /** NIU générés par sexe et par tranche d'âge (pyramide), pour le Togo ou une région. */
    @GetMapping("/age-sexe")
    public AgeSexe ageSexe(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return service.ageSexe(du, au, zone);
    }

    /** Où s'arrêtent les paquets : rejets et échecs par étape d'arrêt, au jour de réception. */
    @GetMapping("/etapes")
    public ArretsParEtape etapes(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return traitement.etapes(du, au, zone);
    }

    /**
     * Où s'arrêtent les paquets, par étape et motif (status_comment de MOSIP rangé par le catalogue) : rejets et échecs
     * au jour de réception, en cours dont bloqués (stock).
     */
    @GetMapping("/motifs")
    public MotifsArret motifs(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return traitement.motifs(du, au, zone);
    }

    /** Paquets en cours par étape, dont bloqués depuis plus de 30 jours (stock à l'heure du dernier calcul). */
    @GetMapping("/en-cours")
    public PaquetsEnCours enCours(
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return traitement.enCours(zone);
    }

    /** Délais : réception → NIU (médiane, 90e centile) et enrôlement → réception (dont moins de 24 h), en heures. */
    @GetMapping("/delais")
    public DelaisTraitement delais(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return traitement.delais(du, au, zone);
    }

    /** Paquets synchronisés par le poste, pas encore reçus par MOSIP (stock à l'heure du dernier calcul). */
    @GetMapping("/synchronisation")
    public SynchronisationNonRecue synchronisation(
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return traitement.synchronisation(zone);
    }

    /**
     * Top des centres : les cinq premiers selon les inscriptions, les échecs, les rejets, ou la remontée la plus lente
     * (paquets synchronisés non reçus depuis plus de 7 jours, stock à l'heure du calcul).
     */
    @GetMapping("/centres")
    public TopCentres centres(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone,
            @RequestParam(defaultValue = "inscriptions") @Pattern(regexp = "inscriptions|echecs|rejets|remontee")
            String classement) {
        return service.centres(du, au, zone, classement);
    }
}
