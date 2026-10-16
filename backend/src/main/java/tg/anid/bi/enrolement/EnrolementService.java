package tg.anid.bi.enrolement;

import java.time.LocalDate;

import org.springframework.stereotype.Service;

import tg.anid.bi.commun.PorteeUtilisateur;
import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.commun.RessourceIntrouvable;

@Service
public class EnrolementService {

    static final String ENSEMBLE_DU_TOGO = "Ensemble du Togo";

    private final EnrolementRepository repository;
    private final PorteeUtilisateur portee;

    public EnrolementService(EnrolementRepository repository, PorteeUtilisateur portee) {
        this.repository = repository;
        this.portee = portee;
    }

    /** Devenir des inscriptions sur la période, dans la portée de l'utilisateur. */
    public DevenirInscriptions devenir(LocalDate du, LocalDate au, String zoneDemandee) {
        if (du != null && au != null && du.isAfter(au)) {
            throw new RequeteInvalide("La date « du » doit précéder la date « au ».");
        }
        String zone = portee.zoneEffective(zoneDemandee);
        String perimetre = zone == null
                ? ENSEMBLE_DU_TOGO
                : repository.nomZone(zone).orElseThrow(() -> new RessourceIntrouvable("Zone inconnue : " + zone));
        EnrolementRepository.Totaux t = repository.devenir(du, au, zone);
        return new DevenirInscriptions(perimetre, du, au, t.inscriptions(), t.niuGeneres(), t.enCours(),
                t.echouees(), t.rejetees(), t.nonClassees());
    }
}
