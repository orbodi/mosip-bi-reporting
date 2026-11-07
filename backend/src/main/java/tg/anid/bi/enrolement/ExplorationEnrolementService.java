package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.util.List;

import org.springframework.stereotype.Service;

import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.commun.RessourceIntrouvable;

/**
 * Onglet Enrôlement de l'Exploration (lot E1, 06/11/2026) : type de demande, ventilations par année, mois et type.
 * Une pré-inscription n'a pas de type de demande : ses chiffres sont retirés (null) dès qu'un type est filtré ou
 * ventilé.
 */
@Service
public class ExplorationEnrolementService {

    static final String ENSEMBLE_DU_TOGO = "Ensemble du Togo";

    private final ExplorationEnrolementRepository repository;
    private final EnrolementRepository enrolement;

    public ExplorationEnrolementService(ExplorationEnrolementRepository repository, EnrolementRepository enrolement) {
        this.repository = repository;
        this.enrolement = enrolement;
    }

    public ExplorationEnrolement exploration(LocalDate du, LocalDate au, String zoneDemandee, String typeDemande,
                                             String par) {
        if (du != null && au != null && du.isAfter(au)) {
            throw new RequeteInvalide("La date « du » doit précéder la date « au ».");
        }
        String zone = zoneDemandee == null || zoneDemandee.isBlank() ? null : zoneDemandee;
        String type = typeDemande == null || typeDemande.isBlank() ? null : typeDemande;
        String perimetre = zone == null
                ? ENSEMBLE_DU_TOGO
                : enrolement.nomZone(zone).orElseThrow(() -> new RessourceIntrouvable("Zone inconnue : " + zone));
        String v = par == null || par.isBlank() ? "total" : par;
        List<ExplorationEnrolement.Ligne> lignes = switch (v) {
            case "total" -> List.of();
            case "sous" -> repository.lignesParSousZone(du, au, zone, type);
            case "type" -> repository.lignesParType(du, au, zone, type);
            case "annee", "mois" -> repository.lignesParTemps(du, au, zone, type, v);
            default -> throw new RequeteInvalide("Ventilation inconnue : sous, annee, mois, type ou total.");
        };
        ExplorationEnrolement.Chiffres total = repository.total(du, au, zone, type);
        if (type != null || "type".equals(v)) {
            total = total.sansPreinscriptions();
            lignes = lignes.stream().map(ExplorationEnrolement.Ligne::sansPreinscriptions).toList();
        }
        return new ExplorationEnrolement(perimetre, zone, du, au, type, v, lignes, total,
                "total".equals(v) ? repository.types() : List.of());
    }
}
