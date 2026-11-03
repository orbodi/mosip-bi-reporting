package tg.anid.bi.cartes;

import java.time.Clock;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.IntStream;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.commun.RessourceIntrouvable;
import tg.anid.bi.enrolement.EnrolementRepository;
import tg.anid.bi.enrolement.EnrolementService;
import tg.anid.bi.enrolement.Territoire;

/**
 * Page Impression des cartes (docs/indicateurs.md, section Impression des cartes). Deux lectures « cohorte » :
 * commandes au jour de réception (demandes, en attente, rejetées, annulées), cartes au jour d'expédition (expédiées,
 * remises, à remettre, délai, ancienneté, territoire, top des centres). Chaque utilisateur lit tout le Togo
 * (décision du 25/10/2026) ; {@code zone} accepte un code de tout niveau.
 */
@Service
public class CartesService {

    static final String ENSEMBLE_DU_TOGO = "Ensemble du Togo";
    static final ZoneId TOGO = ZoneId.of("Africa/Lome");
    static final int NOMBRE_SEMAINES = 12;
    static final int TAILLE_TOP = 5;
    /** Tranches d'ancienneté des cartes à remettre (jours depuis l'expédition), dans l'ordre du bloc. */
    static final List<CartesEnAttente.Tranche> TRANCHES = List.of(
            new CartesEnAttente.Tranche("moins_30j", 0, 30, 0),
            new CartesEnAttente.Tranche("30_90j", 30, 90, 0),
            new CartesEnAttente.Tranche("90_180j", 90, 180, 0),
            new CartesEnAttente.Tranche("plus_180j", 180, null, 0));

    private final CartesRepository repository;
    private final EnrolementRepository zones;
    private final Clock horloge;

    @Autowired
    public CartesService(CartesRepository repository, EnrolementRepository zones) {
        this(repository, zones, Clock.system(TOGO));
    }

    CartesService(CartesRepository repository, EnrolementRepository zones, Clock horloge) {
        this.repository = repository;
        this.zones = zones;
        this.horloge = horloge;
    }

    /** Bloc « Impression et remise » sur la période, dans la zone demandée (tout le Togo par défaut). */
    public ImpressionRemise impression(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = zone(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        if (!repository.disponible()) {
            return ImpressionRemise.nonDisponible(perimetre, du, au);
        }
        CartesRepository.TotauxDemandes d = repository.demandes(du, au, zone);
        CartesRepository.TotauxCartes c = repository.cartes(du, au, zone);
        Integer delai = repository.delaiMedianJours(du, au, zone).orElse(null);
        return new ImpressionRemise(perimetre, du, au, true, d.demandes(), d.envoyees(), d.enAttente(), d.rejetees(),
                d.nonClassees(), d.annulees(), d.derniereRejetee(), c.expediees(), c.remises(),
                c.remisesHorsLigne(), c.remisesEnLigne(), c.remisesSupport(), c.remisesAutre(), c.aRemettre(), delai);
    }

    /**
     * Demandes, cartes imprimées, demandes rejetées et annulées des 12 semaines complètes qui finissent au plus tard
     * à la fin de la période (ou à la dernière donnée d'impression).
     */
    public ImpressionsParSemaine semaines(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = zone(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        Optional<LocalDate> derniere = repository.derniereDonnee();
        if (derniere.isEmpty()) {
            return new ImpressionsParSemaine(perimetre, du, au, List.of());
        }
        LocalDate fin = au == null || au.isAfter(derniere.get()) ? derniere.get() : au;
        List<LocalDate> lundis = EnrolementService.lundisDesSemainesCompletes(fin, NOMBRE_SEMAINES);
        LocalDate debut = lundis.getFirst();
        LocalDate dernierDimanche = lundis.getLast().plusDays(6);
        Map<LocalDate, long[]> demandes = repository.demandesParSemaine(debut, dernierDimanche, zone);
        Map<LocalDate, Long> expediees = repository.expedieesParSemaine(debut, dernierDimanche, zone);
        long[] aucune = {0, 0, 0};
        List<ImpressionsParSemaine.Semaine> semaines = lundis.stream()
                .map(lundi -> {
                    long[] d = demandes.getOrDefault(lundi, aucune);
                    return new ImpressionsParSemaine.Semaine(lundi, EnrolementService.touchePeriode(lundi, du, au),
                            d[0], expediees.getOrDefault(lundi, 0L), d[1], d[2]);
                })
                .toList();
        return new ImpressionsParSemaine(perimetre, du, au, semaines);
    }

    /** Cartes expédiées, remises et à remettre de la zone et de chacune de ses sous-zones directes. */
    public TerritoireCartes territoire(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = zone(zoneDemandee);
        String perimetre = ENSEMBLE_DU_TOGO;
        String niveau = null;
        List<Territoire.ZoneParente> ascendants = List.of();
        if (zone != null) {
            EnrolementRepository.ZoneConnue connue = zones.zone(zone)
                    .orElseThrow(() -> new RessourceIntrouvable("Zone inconnue : " + zone));
            perimetre = connue.nom();
            niveau = connue.niveau();
            ascendants = zones.ascendants(zone);
        }
        CartesRepository.TotauxCartes c = repository.cartes(du, au, zone);
        return new TerritoireCartes(perimetre, zone, niveau, ascendants, du, au, c.expediees(), c.remises(),
                c.aRemettre(), repository.sousZones(du, au, zone));
    }

    /** Cartes à remettre par temps écoulé depuis l'expédition, au jour d'aujourd'hui (heure du Togo). */
    public CartesEnAttente attente(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = zone(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        LocalDate aujourdhui = LocalDate.now(horloge);
        Map<String, Long> parTranche = repository.aRemettreParAnciennete(du, au, zone, aujourdhui);
        List<CartesEnAttente.Tranche> tranches = TRANCHES.stream()
                .map(t -> new CartesEnAttente.Tranche(t.code(), t.depuisJours(), t.avantJours(),
                        parTranche.getOrDefault(t.code(), 0L)))
                .toList();
        long total = tranches.stream().mapToLong(CartesEnAttente.Tranche::cartes).sum();
        return new CartesEnAttente(perimetre, du, au, aujourdhui, total, tranches);
    }

    /** Les cinq centres de la zone qui ont remis le plus de cartes. */
    public TopCentresCartes centres(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = zone(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        List<CartesRepository.Centre> lignes = repository.topCentres(du, au, zone, TAILLE_TOP);
        List<TopCentresCartes.CentreClasse> centres = IntStream.range(0, lignes.size())
                .mapToObj(i -> {
                    CartesRepository.Centre c = lignes.get(i);
                    return new TopCentresCartes.CentreClasse(i + 1, c.code(), c.nom(), c.prefecture(), c.region(),
                            c.remises(), c.expediees());
                })
                .toList();
        return new TopCentresCartes(perimetre, centres);
    }

    /** Commandes annulées par motif (comptées à part), au jour de réception de la commande. */
    public AnnulationsParMotif annulations(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = zone(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        List<AnnulationsParMotif.Motif> motifs = repository.annulationsParMotif(du, au, zone);
        long total = motifs.stream().mapToLong(AnnulationsParMotif.Motif::demandes).sum();
        return new AnnulationsParMotif(perimetre, du, au, total, motifs);
    }

    private static String zone(String zoneDemandee) {
        return zoneDemandee == null || zoneDemandee.isBlank() ? null : zoneDemandee;
    }

    private static void verifierOrdre(LocalDate du, LocalDate au) {
        if (du != null && au != null && du.isAfter(au)) {
            throw new RequeteInvalide("La date « du » doit précéder la date « au ».");
        }
    }

    private String nomPerimetre(String zone) {
        return zone == null
                ? ENSEMBLE_DU_TOGO
                : zones.nomZone(zone).orElseThrow(() -> new RessourceIntrouvable("Zone inconnue : " + zone));
    }
}
