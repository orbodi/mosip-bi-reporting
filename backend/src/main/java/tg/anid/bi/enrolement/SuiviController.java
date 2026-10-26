package tg.anid.bi.enrolement;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/enrolement")
public class SuiviController {

    private final SuiviService service;

    public SuiviController(SuiviService service) {
        this.service = service;
    }

    /**
     * Suivi d'un dossier : le RID (29 chiffres) dans le corps, jamais dans l'adresse. Réponses : 200 avec le dossier,
     * 400 si le RID n'a pas 29 chiffres, 404 s'il ne correspond à aucun dossier, 503 si le suivi n'est pas configuré.
     */
    @PostMapping("/suivi")
    public SuiviDossier suivre(@RequestBody DemandeSuivi demande) {
        return service.suivre(demande.rid());
    }
}
