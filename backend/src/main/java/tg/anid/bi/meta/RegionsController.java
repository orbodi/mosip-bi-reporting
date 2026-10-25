package tg.anid.bi.meta;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/meta/regions")
public class RegionsController {

    private final RegionsRepository repository;

    public RegionsController(RegionsRepository repository) {
        this.repository = repository;
    }

    /** Les régions, du nord au sud. Chaque utilisateur a accès à tout le Togo (décision du 25/10/2026). */
    @GetMapping
    public List<Region> regions() {
        return repository.regions();
    }
}
