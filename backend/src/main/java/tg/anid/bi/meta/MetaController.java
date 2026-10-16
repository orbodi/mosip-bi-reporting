package tg.anid.bi.meta;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/meta")
public class MetaController {

    static final String APPLICATION = "BI Reporting ANID";

    private final MetaRepository repository;

    public MetaController(MetaRepository repository) {
        this.repository = repository;
    }

    /** Fraîcheur de chaque source, dans l'ordre d'affichage. */
    @GetMapping
    public Meta meta() {
        return new Meta(APPLICATION, repository.fraicheurs());
    }
}
