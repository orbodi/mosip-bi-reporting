package tg.anid.bi.authentifications;

import java.time.LocalDate;

import jakarta.validation.constraints.Pattern;

import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * Page Authentifications (lot 9). Période : jour d'enregistrement de l'authentification par IDA. Pas de paramètre
 * zone : une authentification n'a pas de territoire.
 */
@RestController
@RequestMapping("/api/v1/authentifications")
public class AuthentificationsController {

    private final AuthentificationsService service;

    public AuthentificationsController(AuthentificationsService service) {
        this.service = service;
    }

    /** Requêtes d'authentification des usagers : statut, type, partenaires raccordés, demandes et codes OTP. */
    @GetMapping("/usagers")
    public RequetesUsagers usagers(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au) {
        return service.usagers(du, au);
    }

    /** Requêtes et échecs des usagers par type d'authentification. */
    @GetMapping("/types")
    public TypesAuthentification types(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au) {
        return service.types(du, au);
    }

    /** Causes des échecs des usagers, ou du traitement des paquets ({@code perimetre=paquets}). */
    @GetMapping("/causes")
    public CausesEchec causes(
            @RequestParam(required = false) @Pattern(regexp = "usagers|paquets") String perimetre,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au) {
        return service.causes(perimetre, du, au);
    }

    /** Partenaires et canaux des usagers. */
    @GetMapping("/partenaires")
    public PartenairesEtCanaux partenaires(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au) {
        return service.partenaires(du, au);
    }

    /** Requêtes réussies et échouées des usagers des 12 semaines complètes jusqu'à la fin de la période. */
    @GetMapping("/semaines")
    public AuthentificationsParSemaine semaines(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au) {
        return service.semaines(du, au);
    }

    /** Vérifications biométriques du traitement des paquets (bloc à part). */
    @GetMapping("/paquets")
    public VerificationsPaquets paquets(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au) {
        return service.paquets(du, au);
    }
}
