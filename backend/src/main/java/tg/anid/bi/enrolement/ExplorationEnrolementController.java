package tg.anid.bi.enrolement;

import java.time.LocalDate;

import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Onglet Enrôlement de l'Exploration (lots E1 et E2, 06 et 07/11/2026). */
@RestController
@RequestMapping("/api/v1/enrolement")
public class ExplorationEnrolementController {

    private final ExplorationEnrolementService service;

    public ExplorationEnrolementController(ExplorationEnrolementService service) {
        this.service = service;
    }

    /**
     * Inscriptions, devenir et pré-inscriptions de la zone, filtrées par type de demande MOSIP, sexe (F, H, I),
     * tranche d'âge et nationalité, par sous-zone directe, année, mois, type, sexe, tranche d'âge ou nationalité
     * ({@code par} : sous, annee, mois, type, sexe, age, nationalite ou total).
     */
    @GetMapping("/exploration")
    public ExplorationEnrolement exploration(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone,
            @RequestParam(required = false) @Pattern(regexp = "[A-Z_]{1,40}") String type,
            @RequestParam(required = false) @Pattern(regexp = "[FHI]") String sexe,
            @RequestParam(required = false) @Pattern(regexp = "0-5|6-14|15-18|19-25|26-35|36-45|46-60|60\\+|inconnu")
            String age,
            @RequestParam(required = false) @Size(max = 80) String nationalite,
            @RequestParam(required = false) @Pattern(regexp = "sous|annee|mois|type|sexe|age|nationalite|total")
            String par) {
        return service.exploration(du, au, zone, new ExplorationEnrolementRepository.Filtres(type, sexe, age,
                nationalite), par);
    }
}
