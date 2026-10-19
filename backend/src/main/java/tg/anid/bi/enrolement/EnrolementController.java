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

    public EnrolementController(EnrolementService service) {
        this.service = service;
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

    /** Territoire : totaux de la zone (tout le Togo par défaut) et une ligne par sous-zone directe. */
    @GetMapping("/territoire")
    public Territoire territoire(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return service.territoire(du, au, zone);
    }

    /** Top des centres : les cinq premiers selon les inscriptions, les échecs ou les rejets. */
    @GetMapping("/centres")
    public TopCentres centres(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone,
            @RequestParam(defaultValue = "inscriptions") @Pattern(regexp = "inscriptions|echecs|rejets")
            String classement) {
        return service.centres(du, au, zone, classement);
    }
}
