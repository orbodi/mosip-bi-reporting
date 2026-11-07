package tg.anid.bi.enrolement;

import java.time.LocalDate;

import jakarta.validation.constraints.Pattern;

import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Onglet Enrôlement de l'Exploration (lot E1, 06/11/2026). */
@RestController
@RequestMapping("/api/v1/enrolement")
public class ExplorationEnrolementController {

    private final ExplorationEnrolementService service;

    public ExplorationEnrolementController(ExplorationEnrolementService service) {
        this.service = service;
    }

    /**
     * Inscriptions, devenir et pré-inscriptions de la zone, filtrées par type de demande MOSIP, par sous-zone directe,
     * par année, par mois ou par type de demande ({@code par} : sous, annee, mois, type ou total).
     */
    @GetMapping("/exploration")
    public ExplorationEnrolement exploration(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone,
            @RequestParam(required = false) @Pattern(regexp = "[A-Z_]{1,40}") String type,
            @RequestParam(required = false) @Pattern(regexp = "sous|annee|mois|type|total") String par) {
        return service.exploration(du, au, zone, type, par);
    }
}
