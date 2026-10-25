package tg.anid.bi.enrolement;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Collectors;
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
    /** Nationalité des demandes non enrichies ou sans nationalité (valeur de bi.fait_preinscription_profil_jour). */
    static final String NATIONALITE_NON_RENSEIGNEE = "Non renseignée";
    static final String NATIONALITE_AUTRES = "Autres";
    /** Tranche des pré-inscrits dont le sexe est connu mais pas l'âge (dernière ligne de la pyramide). */
    static final String TRANCHE_AGE_INCONNU = "inconnu";
    static final Set<String> CLASSEMENTS = Set.of("inscriptions", "echecs", "rejets");
    /** Tranches d'âge de la pyramide (maquette Enrôlement), de la plus jeune à la plus âgée. */
    static final List<String> TRANCHES_AGE = List.of("0-5", "6-14", "15-18", "19-25", "26-35", "36-45", "46-60",
            "60+");

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
        Map<String, Integer> delais = repository.delaisMedians(du, au, zone);
        List<Territoire.LigneZone> lignes = repository.sousZones(du, au, zone).stream()
                .map(l -> l.avecDelai(delais.get(l.code())))
                .toList();
        return new Territoire(perimetre, zone, du, au, t.inscriptions(), t.niuGeneres(), t.enCours(),
                t.echouees(), t.rejetees(), t.nonClassees(), repository.preinscriptionsZone(du, au, zone),
                delais.get(EnrolementRepository.ZONE_ENTIERE), lignes);
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
     * Pré-inscriptions créées sur la période. Nationales : une demande n'a pas de territoire, donc un utilisateur
     * régional reçoit le bloc sans chiffres (jamais les chiffres nationaux). Sans données du pipeline, le bloc est
     * signalé non disponible.
     */
    public Preinscriptions preinscriptions(LocalDate du, LocalDate au) {
        verifierOrdre(du, au);
        String zone = portee.zoneEffective(null);
        if (zone != null) {
            return Preinscriptions.nonDisponible(nomPerimetre(zone), du, au);
        }
        if (!repository.preinscriptionsDisponibles()) {
            return Preinscriptions.nonDisponible(ENSEMBLE_DU_TOGO, du, au);
        }
        EnrolementRepository.TotauxPreinscription t = repository.preinscriptions(du, au);
        // Sexe : non disponible (null) tant qu'aucune demande de la période n'a de sexe connu.
        boolean sexeConnu = t.femmes() + t.hommes() > 0;
        return new Preinscriptions(ENSEMBLE_DU_TOGO, du, au, true, t.demandes(), t.reservees(), t.enAttente(),
                t.expirees(), t.annulees(), t.honorees(), t.nonClassees(),
                sexeConnu ? t.femmes() : null, sexeConnu ? t.hommes() : null,
                repository.derniereDemande().orElse(null));
    }

    /**
     * NIU générés par sexe et tranche d'âge sur la période, dans la région demandée (ou celle de l'utilisateur). Le
     * profil anonymisé ne situe un NIU qu'à la région : une préfecture ou un centre est refusé.
     */
    public AgeSexe ageSexe(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = portee.zoneEffective(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        if (zone != null && !repository.estRegion(zone)) {
            throw new RequeteInvalide("La répartition par âge et par sexe n'existe que par région.");
        }
        if (!repository.profilsDisponibles()) {
            List<AgeSexe.Tranche> vides = TRANCHES_AGE.stream()
                    .map(t -> new AgeSexe.Tranche(t, null, null))
                    .toList();
            return new AgeSexe(perimetre, du, au, false, vides, null);
        }
        List<EnrolementRepository.CaseProfil> cases = repository.niuParSexeEtAge(du, au, zone);
        List<AgeSexe.Tranche> tranches = TRANCHES_AGE.stream()
                .map(t -> new AgeSexe.Tranche(t, somme(cases, "F", t), somme(cases, "H", t)))
                .toList();
        long nonRenseignes = cases.stream()
                .filter(c -> (!"F".equals(c.sexe()) && !"H".equals(c.sexe())) || !TRANCHES_AGE.contains(c.trancheAge()))
                .mapToLong(EnrolementRepository.CaseProfil::niuGeneres)
                .sum();
        return new AgeSexe(perimetre, du, au, true, tranches, nonRenseignes);
    }

    /**
     * Pré-inscriptions par tranche d'âge et sexe, et par nationalité (les {@value #TAILLE_TOP} premières, puis
     * « Autres » et « Non renseignée »). Nationales, comme le bloc « Pré-inscription ».
     */
    public ProfilPreinscriptions profilPreinscriptions(LocalDate du, LocalDate au) {
        verifierOrdre(du, au);
        String zone = portee.zoneEffective(null);
        List<String> tranchesProfil = new ArrayList<>(TRANCHES_AGE);
        tranchesProfil.add(TRANCHE_AGE_INCONNU);
        if (zone != null) {
            return ProfilPreinscriptions.nonDisponible(nomPerimetre(zone), du, au, tranchesProfil);
        }
        if (!repository.profilPreinscriptionsDisponible()) {
            return ProfilPreinscriptions.nonDisponible(ENSEMBLE_DU_TOGO, du, au, tranchesProfil);
        }
        List<EnrolementRepository.CasePreinscription> cases = repository.preinscriptionsParProfil(du, au);
        // Toute tranche hors des huit (âge absent ou invalide) compte dans « inconnu ».
        List<AgeSexe.Tranche> tranches = tranchesProfil.stream()
                .map(t -> new AgeSexe.Tranche(t, sommeDemandes(cases, "F", t), sommeDemandes(cases, "H", t)))
                .toList();
        long nonRenseignes = cases.stream()
                .filter(c -> !"F".equals(c.sexe()) && !"H".equals(c.sexe()))
                .mapToLong(EnrolementRepository.CasePreinscription::demandes)
                .sum();
        return new ProfilPreinscriptions(ENSEMBLE_DU_TOGO, du, au, true, tranches, nonRenseignes,
                nationalites(cases));
    }

    /** Les {@value #TAILLE_TOP} nationalités les plus nombreuses, puis « Autres » et « Non renseignée » si non nulles. */
    static List<ProfilPreinscriptions.Nationalite> nationalites(List<EnrolementRepository.CasePreinscription> cases) {
        Map<String, Long> parNationalite = cases.stream().collect(Collectors.groupingBy(
                EnrolementRepository.CasePreinscription::nationalite, TreeMap::new,
                Collectors.summingLong(EnrolementRepository.CasePreinscription::demandes)));
        long nonRenseignee = parNationalite.getOrDefault(NATIONALITE_NON_RENSEIGNEE, 0L);
        List<ProfilPreinscriptions.Nationalite> connues = parNationalite.entrySet().stream()
                .filter(e -> !NATIONALITE_NON_RENSEIGNEE.equals(e.getKey()) && e.getValue() > 0)
                .map(e -> new ProfilPreinscriptions.Nationalite(e.getKey(), e.getValue()))
                .sorted(Comparator.comparingLong(ProfilPreinscriptions.Nationalite::demandes).reversed()
                        .thenComparing(ProfilPreinscriptions.Nationalite::nom))
                .toList();
        List<ProfilPreinscriptions.Nationalite> resultat = new ArrayList<>(connues.stream().limit(TAILLE_TOP).toList());
        long autres = connues.stream().skip(TAILLE_TOP).mapToLong(ProfilPreinscriptions.Nationalite::demandes).sum();
        if (autres > 0) {
            resultat.add(new ProfilPreinscriptions.Nationalite(NATIONALITE_AUTRES, autres));
        }
        if (nonRenseignee > 0) {
            resultat.add(new ProfilPreinscriptions.Nationalite(NATIONALITE_NON_RENSEIGNEE, nonRenseignee));
        }
        return List.copyOf(resultat);
    }

    private static long sommeDemandes(List<EnrolementRepository.CasePreinscription> cases, String sexe,
                                      String tranche) {
        return cases.stream()
                .filter(c -> sexe.equals(c.sexe()))
                .filter(c -> TRANCHE_AGE_INCONNU.equals(tranche)
                        ? !TRANCHES_AGE.contains(c.trancheAge())
                        : tranche.equals(c.trancheAge()))
                .mapToLong(EnrolementRepository.CasePreinscription::demandes)
                .sum();
    }

    private static long somme(List<EnrolementRepository.CaseProfil> cases, String sexe, String tranche) {
        return cases.stream()
                .filter(c -> sexe.equals(c.sexe()) && tranche.equals(c.trancheAge()))
                .mapToLong(EnrolementRepository.CaseProfil::niuGeneres)
                .sum();
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
