package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.util.List;

import org.springframework.stereotype.Service;

import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.commun.RessourceIntrouvable;

/**
 * Onglet Enrôlement de l'Exploration (lots E1 et E2, 06 et 07/11/2026) : type de demande, sexe, tranche d'âge et
 * nationalité ; ventilations par sous-zone, année, mois, type, sexe, tranche d'âge et nationalité. Une pré-inscription
 * n'a ni type de demande, ni profil par centre : ses chiffres sont retirés (null) dès qu'un de ces filtres ou une de
 * ces ventilations est demandé.
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

    public ExplorationEnrolement exploration(LocalDate du, LocalDate au, String zoneDemandee,
                                             ExplorationEnrolementRepository.Filtres filtresDemandes, String par) {
        if (du != null && au != null && du.isAfter(au)) {
            throw new RequeteInvalide("La date « du » doit précéder la date « au ».");
        }
        String zone = vide(zoneDemandee);
        ExplorationEnrolementRepository.Filtres filtres = filtresDemandes == null
                ? ExplorationEnrolementRepository.Filtres.AUCUN
                : new ExplorationEnrolementRepository.Filtres(vide(filtresDemandes.type()),
                        vide(filtresDemandes.sexe()), vide(filtresDemandes.age()), vide(filtresDemandes.nationalite()));
        String perimetre = zone == null
                ? ENSEMBLE_DU_TOGO
                : enrolement.nomZone(zone).orElseThrow(() -> new RessourceIntrouvable("Zone inconnue : " + zone));
        String v = par == null || par.isBlank() ? "total" : par;
        List<ExplorationEnrolement.Ligne> lignes;
        if ("total".equals(v)) {
            lignes = List.of();
        } else if ("sous".equals(v)) {
            lignes = repository.lignesParSousZone(du, au, zone, filtres);
        } else if (ExplorationEnrolementRepository.VENTILATIONS_TEMPS.containsKey(v)) {
            lignes = repository.lignesParTemps(du, au, zone, filtres, v);
        } else if (ExplorationEnrolementRepository.VENTILATIONS_COLONNE.containsKey(v)) {
            lignes = repository.lignesParColonne(du, au, zone, filtres, v);
        } else {
            throw new RequeteInvalide(
                    "Ventilation inconnue : sous, annee, mois, type, sexe, age, nationalite ou total.");
        }
        ExplorationEnrolement.Chiffres total = repository.total(du, au, zone, filtres);
        if (filtres.type() != null || filtres.profil() || ExplorationEnrolementRepository.VENTILATIONS_COLONNE
                .containsKey(v)) {
            total = total.sansPreinscriptions();
            lignes = lignes.stream().map(ExplorationEnrolement.Ligne::sansPreinscriptions).toList();
        }
        boolean valeurs = "total".equals(v);
        return new ExplorationEnrolement(perimetre, zone, du, au, filtres.type(), v, lignes, total,
                valeurs ? repository.types() : List.of(), valeurs ? repository.nationalites() : List.of());
    }

    private static String vide(String valeur) {
        return valeur == null || valeur.isBlank() ? null : valeur;
    }
}
