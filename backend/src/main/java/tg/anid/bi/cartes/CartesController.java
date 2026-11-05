package tg.anid.bi.cartes;

import java.time.LocalDate;

import jakarta.validation.constraints.Pattern;

import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * Page Impression des cartes (lot 8). Période : jour de réception de la commande pour les demandes et les
 * annulations, jour d'expédition pour les cartes (expédiées, remises, à remettre, délai, territoire, centres).
 */
@RestController
@RequestMapping("/api/v1/cartes")
public class CartesController {

    private final CartesService service;

    public CartesController(CartesService service) {
        this.service = service;
    }

    /** Impression et remise : demandes par statut, annulées, cartes expédiées, remises par mode, à remettre, délai. */
    @GetMapping("/impression")
    public ImpressionRemise impression(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return service.impression(du, au, zone);
    }

    /** Demandes, cartes imprimées, rejetées et annulées des 12 semaines complètes jusqu'à la fin de la période. */
    @GetMapping("/semaines")
    public ImpressionsParSemaine semaines(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return service.semaines(du, au, zone);
    }

    /** Cartes à remettre par région : totaux de la zone et une ligne par sous-zone directe. */
    @GetMapping("/territoire")
    public TerritoireCartes territoire(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return service.territoire(du, au, zone);
    }

    /** Depuis quand ces cartes attendent : cartes à remettre par temps écoulé depuis l'expédition. */
    @GetMapping("/attente")
    public CartesEnAttente attente(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return service.attente(du, au, zone);
    }

    /** Top des centres : les cinq qui ont remis le plus de cartes. */
    @GetMapping("/centres")
    public TopCentresCartes centres(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return service.centres(du, au, zone);
    }

    /** Commandes annulées par motif, comptées à part. */
    @GetMapping("/annulations")
    public AnnulationsParMotif annulations(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone) {
        return service.annulations(du, au, zone);
    }

    /**
     * Onglet Impression des cartes de l'Exploration : demandes, cartes expédiées, remises et à remettre de la zone,
     * par sous-zone directe, par année ou par mois ({@code par} : sous, annee, mois ou total).
     */
    @GetMapping("/exploration")
    public ExplorationCartes exploration(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate du,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate au,
            @RequestParam(required = false) @Pattern(regexp = "[A-Za-z0-9_-]{1,40}") String zone,
            @RequestParam(required = false) @Pattern(regexp = "sous|annee|mois|total") String par) {
        return service.exploration(du, au, zone, par);
    }
}
