package tg.anid.bi.meta;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import tg.anid.bi.commun.PorteeUtilisateur;

@RestController
@RequestMapping("/api/v1/meta/regions")
public class RegionsController {

    private final RegionsRepository repository;
    private final PorteeUtilisateur portee;

    public RegionsController(RegionsRepository repository, PorteeUtilisateur portee) {
        this.repository = repository;
        this.portee = portee;
    }

    /**
     * Choix du filtre Région, du nord au sud : toutes les régions pour un utilisateur national, la sienne seulement
     * pour un utilisateur régional (portée appliquée par l'API, jamais seulement par le front).
     */
    @GetMapping
    public List<Region> regions() {
        String zone = portee.zoneEffective(null);
        List<Region> toutes = repository.regions();
        return zone == null ? toutes : toutes.stream().filter(r -> r.code().equals(zone)).toList();
    }
}
