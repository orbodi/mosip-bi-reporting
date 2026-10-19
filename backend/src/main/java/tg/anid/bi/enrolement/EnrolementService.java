package tg.anid.bi.enrolement;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.IntStream;

import org.springframework.stereotype.Service;

import tg.anid.bi.commun.PorteeUtilisateur;
import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.commun.RessourceIntrouvable;

@Service
public class EnrolementService {

    static final String ENSEMBLE_DU_TOGO = "Ensemble du Togo";
    static final int NOMBRE_SEMAINES = 12;
    static final int TAILLE_TOP = 5;
    static final Set<String> CLASSEMENTS = Set.of("inscriptions", "echecs", "rejets");

    private final EnrolementRepository repository;
    private final PorteeUtilisateur portee;

    public EnrolementService(EnrolementRepository repository, PorteeUtilisateur portee) {
        this.repository = repository;
        this.portee = portee;
    }

    /** Devenir des inscriptions sur la période, dans la portée de l'utilisateur. */
    public DevenirInscriptions devenir(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = portee.zoneEffective(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        EnrolementRepository.Totaux t = repository.devenir(du, au, zone);
        return new DevenirInscriptions(perimetre, du, au, t.inscriptions(), t.niuGeneres(), t.enCours(),
                t.echouees(), t.rejetees(), t.nonClassees());
    }

    /**
     * Inscriptions et NIU des 12 semaines complètes qui finissent au plus tard à la fin de la période (ou à la
     * dernière donnée), dans la portée de l'utilisateur.
     */
    public InscriptionsParSemaine semaines(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = portee.zoneEffective(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        boolean niuDisponibles = repository.niuDisponibles();
        Optional<LocalDate> derniere = repository.derniereDonnee();
        if (derniere.isEmpty()) {
            return new InscriptionsParSemaine(perimetre, du, au, niuDisponibles, List.of());
        }
        LocalDate fin = au == null || au.isAfter(derniere.get()) ? derniere.get() : au;
        List<LocalDate> lundis = lundisDesSemainesCompletes(fin, NOMBRE_SEMAINES);
        LocalDate debut = lundis.getFirst();
        LocalDate dernierDimanche = lundis.getLast().plusDays(6);
        Map<LocalDate, Long> inscriptions = repository.inscriptionsParSemaine(debut, dernierDimanche, zone);
        Map<LocalDate, Long> niu = repository.niuParSemaine(debut, dernierDimanche, zone);
        List<InscriptionsParSemaine.Semaine> semaines = lundis.stream()
                .map(lundi -> new InscriptionsParSemaine.Semaine(lundi, touchePeriode(lundi, du, au),
                        inscriptions.getOrDefault(lundi, 0L), niu.getOrDefault(lundi, 0L)))
                .toList();
        return new InscriptionsParSemaine(perimetre, du, au, niuDisponibles, semaines);
    }

    /** Totaux de la zone et chiffres de chacune de ses sous-zones directes, dans la portée de l'utilisateur. */
    public Territoire territoire(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = portee.zoneEffective(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        EnrolementRepository.Totaux t = repository.devenir(du, au, zone);
        List<Territoire.LigneZone> lignes = repository.sousZones(du, au, zone);
        return new Territoire(perimetre, zone, du, au, t.inscriptions(), t.niuGeneres(), t.enCours(),
                t.echouees(), t.rejetees(), t.nonClassees(), lignes);
    }

    /** Les cinq premiers centres de la portée selon le classement : inscriptions, echecs ou rejets. */
    public TopCentres centres(LocalDate du, LocalDate au, String zoneDemandee, String classement) {
        verifierOrdre(du, au);
        if (!CLASSEMENTS.contains(classement)) {
            throw new RequeteInvalide("Classement inconnu : choisir inscriptions, echecs ou rejets.");
        }
        String zone = portee.zoneEffective(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        List<EnrolementRepository.Centre> lignes = repository.topCentres(du, au, zone, classement, TAILLE_TOP);
        List<TopCentres.CentreClasse> centres = IntStream.range(0, lignes.size())
                .mapToObj(i -> {
                    EnrolementRepository.Centre c = lignes.get(i);
                    return new TopCentres.CentreClasse(i + 1, c.code(), c.nom(), c.prefecture(), c.region(),
                            c.valeur(), c.inscriptions());
                })
                .toList();
        return new TopCentres(perimetre, classement, centres);
    }

    /**
     * Lundis des {@code nombre} dernières semaines complètes (lundi à dimanche) qui finissent au plus tard le jour
     * {@code fin}, de la plus ancienne à la plus récente. Une semaine en cours n'est jamais comptée.
     */
    static List<LocalDate> lundisDesSemainesCompletes(LocalDate fin, int nombre) {
        LocalDate dernierLundi = fin.getDayOfWeek() == DayOfWeek.SUNDAY
                ? fin.minusDays(6)
                : fin.with(DayOfWeek.MONDAY).minusWeeks(1);
        return IntStream.range(0, nombre)
                .mapToObj(k -> dernierLundi.minusWeeks(nombre - 1L - k))
                .toList();
    }

    /** Vrai si la semaine qui commence ce lundi a au moins un jour dans la période (bornes nulles = non bornée). */
    static boolean touchePeriode(LocalDate lundi, LocalDate du, LocalDate au) {
        return (du == null || !lundi.plusDays(6).isBefore(du)) && (au == null || !lundi.isAfter(au));
    }

    private static void verifierOrdre(LocalDate du, LocalDate au) {
        if (du != null && au != null && du.isAfter(au)) {
            throw new RequeteInvalide("La date « du » doit précéder la date « au ».");
        }
    }

    private String nomPerimetre(String zone) {
        return zone == null
                ? ENSEMBLE_DU_TOGO
                : repository.nomZone(zone).orElseThrow(() -> new RessourceIntrouvable("Zone inconnue : " + zone));
    }
}
