package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.function.ToLongFunction;

import org.springframework.stereotype.Service;

import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.commun.RessourceIntrouvable;

/**
 * Blocs du traitement des paquets de la page Enrôlement (migrations V7, V9) : où s'arrêtent les paquets (par étape ou
 * par motif), paquets en cours, délais, synchronisés non reçus. Chaque utilisateur a accès à tout le Togo (décision
 * du 25/10/2026).
 */
@Service
public class EnrolementTraitementService {

    static final String ENSEMBLE_DU_TOGO = "Ensemble du Togo";
    /** Une étape sous cette part du total (en %) va dans « Autres étapes ». */
    static final int PART_MINIMALE_POURCENT = 1;
    static final String AUTRES_ETAPES = "Autres étapes";
    static final String AUTRES_CAS = "Autres cas";
    /** Ancienneté (jours) au-delà de laquelle un paquet en cours est dit bloqué (stock_en_cours, plus_30j). */
    static final int SEUIL_BLOQUE_JOURS = 30;
    static final String RECEPTION_NIU = "reception_niu";
    static final String ENROLEMENT_RECEPTION = "enrolement_reception";
    static final String NOUVELLE_INSCRIPTION = "NEW";

    private final EnrolementTraitementRepository repository;
    private final EnrolementRepository zones;

    public EnrolementTraitementService(EnrolementTraitementRepository repository, EnrolementRepository zones) {
        this.repository = repository;
        this.zones = zones;
    }

    /** Rejets et échecs par étape d'arrêt sur la période, dans la zone (tout le Togo par défaut). */
    public ArretsParEtape etapes(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = zone(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        List<EnrolementTraitementRepository.ArretEtape> arrets = repository.arretsParEtape(du, au, zone);
        List<ArretsParEtape.Etape> rejets = regrouper(
                arrets.stream().filter(a -> "rejete".equals(a.devenir())).toList(),
                EnrolementTraitementRepository.ArretEtape::inscriptions,
                a -> new ArretsParEtape.Etape(a.etape(), a.libelle(), a.inscriptions()),
                reste -> new ArretsParEtape.Etape(null, AUTRES_ETAPES, somme(reste,
                        EnrolementTraitementRepository.ArretEtape::inscriptions)));
        List<ArretsParEtape.Etape> echecs = regrouper(
                arrets.stream().filter(a -> "echoue".equals(a.devenir())).toList(),
                EnrolementTraitementRepository.ArretEtape::inscriptions,
                a -> new ArretsParEtape.Etape(a.etape(), a.libelle(), a.inscriptions()),
                reste -> new ArretsParEtape.Etape(null, AUTRES_ETAPES, somme(reste,
                        EnrolementTraitementRepository.ArretEtape::inscriptions)));
        return new ArretsParEtape(perimetre, du, au, somme(rejets, ArretsParEtape.Etape::inscriptions),
                somme(echecs, ArretsParEtape.Etape::inscriptions), rejets, echecs);
    }

    /** Paquets en cours par étape, dont bloqués, à l'heure du dernier calcul (stock, sans période). */
    public PaquetsEnCours enCours(String zoneDemandee) {
        String zone = zone(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        List<EnrolementTraitementRepository.EnCoursEtape> lignes = repository.enCoursParEtape(zone);
        List<PaquetsEnCours.Etape> etapes = regrouper(lignes,
                EnrolementTraitementRepository.EnCoursEtape::inscriptions,
                e -> new PaquetsEnCours.Etape(e.etape(), e.libelle(), e.inscriptions(), e.bloques()),
                reste -> new PaquetsEnCours.Etape(null, AUTRES_ETAPES,
                        somme(reste, EnrolementTraitementRepository.EnCoursEtape::inscriptions),
                        somme(reste, EnrolementTraitementRepository.EnCoursEtape::bloques)));
        return new PaquetsEnCours(perimetre, repository.enCoursCalculeLe(), SEUIL_BLOQUE_JOURS,
                somme(etapes, PaquetsEnCours.Etape::inscriptions), somme(etapes, PaquetsEnCours.Etape::bloques),
                etapes);
    }

    /**
     * Rejets et échecs (sur la période) et paquets en cours (stock) par motif, dans la zone : une ligne par motif toutes
     * étapes confondues, du plus fréquent au moins fréquent, les motifs de moins de 1 % du devenir regroupés en
     * « Autres cas ».
     */
    public MotifsArret motifs(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = zone(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        List<EnrolementTraitementRepository.Motif> motifs = repository.parMotif(du, au, zone);
        List<MotifsArret.Ligne> rejets = lignesMotif(motifs, "rejete");
        List<MotifsArret.Ligne> echecs = lignesMotif(motifs, "echoue");
        List<MotifsArret.Ligne> enCours = lignesMotif(motifs, "en_cours");
        return new MotifsArret(perimetre, du, au, repository.enCoursMotifCalculeLe(), SEUIL_BLOQUE_JOURS,
                somme(rejets, MotifsArret.Ligne::inscriptions), somme(echecs, MotifsArret.Ligne::inscriptions),
                somme(enCours, MotifsArret.Ligne::inscriptions), somme(enCours, MotifsArret.Ligne::bloques),
                rejets, echecs, enCours);
    }

    /**
     * Un motif d'un devenir, toutes étapes confondues : la ligne de son étape la plus fréquente, les étapes où il est
     * posé (par leur nom en français : MOSIP donne deux codes, PacketValidatorStage et VALIDATE_PACKET, à la même
     * étape « Validation du paquet ») et ses paquets.
     */
    private record MotifFusionne(EnrolementTraitementRepository.Motif principale, Set<String> etapes,
                                 long inscriptions, long bloques) {

        MotifFusionne(EnrolementTraitementRepository.Motif m) {
            this(m, Set.of(nomEtape(m)), m.inscriptions(), m.bloques());
        }

        MotifFusionne avec(MotifFusionne autre) {
            EnrolementTraitementRepository.Motif p = autre.principale().inscriptions() > principale.inscriptions()
                    ? autre.principale() : principale;
            Set<String> toutes = new HashSet<>(etapes);
            toutes.addAll(autre.etapes());
            return new MotifFusionne(p, Set.copyOf(toutes), inscriptions + autre.inscriptions(),
                    bloques + autre.bloques());
        }

        private static String nomEtape(EnrolementTraitementRepository.Motif m) {
            return m.stageLibelle() != null ? m.stageLibelle() : String.valueOf(m.stage());
        }
    }

    /**
     * Lignes d'un devenir : une par motif (étapes additionnées, étape principale = la plus fréquente), du plus
     * fréquent au moins fréquent (à égalité, l'ordre du dépôt), petits motifs regroupés.
     */
    private static List<MotifsArret.Ligne> lignesMotif(List<EnrolementTraitementRepository.Motif> motifs,
                                                       String devenir) {
        Map<String, MotifFusionne> parMotif = new LinkedHashMap<>();
        motifs.stream().filter(m -> devenir.equals(m.devenir()))
                .forEach(m -> parMotif.merge(m.motif(), new MotifFusionne(m), MotifFusionne::avec));
        List<MotifFusionne> tries = parMotif.values().stream()
                .sorted(Comparator.comparingLong(MotifFusionne::inscriptions).reversed())
                .toList();
        return regrouper(tries, MotifFusionne::inscriptions,
                f -> new MotifsArret.Ligne(f.principale().motif(), f.principale().motifLibelle(),
                        f.principale().motifCommentaire(), f.principale().motifPiste(), f.principale().stage(),
                        f.principale().stageLibelle(), f.etapes().size() - 1, f.inscriptions(), f.bloques()),
                reste -> new MotifsArret.Ligne(null, AUTRES_CAS, null, null, null, null, 0,
                        somme(reste, MotifFusionne::inscriptions), somme(reste, MotifFusionne::bloques)));
    }

    /** Paquets en cours depuis plus de 30 jours dans la zone : « dont bloqués » du bloc « Devenir ». */
    public long bloques(String zoneDemandee) {
        return repository.bloques(zone(zoneDemandee));
    }

    /**
     * Délais sur la période : de la réception au NIU (premières inscriptions, comme le délai médian du Territoire) et
     * de l'enrôlement à la réception (tous les paquets).
     */
    public DelaisTraitement delais(LocalDate du, LocalDate au, String zoneDemandee) {
        verifierOrdre(du, au);
        String zone = zone(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        return new DelaisTraitement(perimetre, du, au,
                mesure(repository.histogramme(RECEPTION_NIU, NOUVELLE_INSCRIPTION, du, au, zone)),
                mesure(repository.histogramme(ENROLEMENT_RECEPTION, null, du, au, zone)));
    }

    /** Synchronisés non reçus dans la zone, à l'heure du dernier calcul (stock, sans période). */
    public SynchronisationNonRecue synchronisation(String zoneDemandee) {
        String zone = zone(zoneDemandee);
        String perimetre = nomPerimetre(zone);
        EnrolementTraitementRepository.StockSynchro s = repository.synchronisationNonRecue(zone);
        return new SynchronisationNonRecue(perimetre, s.calculeLe(), s.nonRecus(), s.plusDe7Jours(),
                s.plusAncienneLe());
    }

    /**
     * Médiane, 90e centile et paquets de moins de 24 h d'un histogramme (classes triées par borne basse) : le centile
     * p est la plus petite classe où le cumul atteint p × total. Sans paquet, médiane et centile sont null.
     */
    static DelaisTraitement.Mesure mesure(List<EnrolementTraitementRepository.Classe> classes) {
        long total = somme(classes, EnrolementTraitementRepository.Classe::paquets);
        long moins24h = classes.stream().filter(c -> c.classeH() < 24)
                .mapToLong(EnrolementTraitementRepository.Classe::paquets).sum();
        return new DelaisTraitement.Mesure(total, centile(classes, total, 50), centile(classes, total, 90),
                moins24h);
    }

    private static Integer centile(List<EnrolementTraitementRepository.Classe> classes, long total, int pourcent) {
        if (total == 0) {
            return null;
        }
        long cumul = 0;
        for (EnrolementTraitementRepository.Classe c : classes) {
            cumul += c.paquets();
            // cumul ≥ pourcent % du total, en entiers (pas d'arrondi flottant).
            if (cumul * 100 >= total * pourcent) {
                return c.classeH();
            }
        }
        return classes.getLast().classeH();
    }

    /**
     * Étapes dans l'ordre reçu ; celles de moins de {@value #PART_MINIMALE_POURCENT} % du total vont dans une ligne
     * « Autres étapes », en dernier. Une seule petite étape reste à son nom (pas de « Autres » pour une étape).
     */
    static <E, R> List<R> regrouper(List<E> etapes, ToLongFunction<E> valeur, Function<E, R> ligne,
                                    Function<List<E>, R> autres) {
        long total = etapes.stream().mapToLong(valeur).sum();
        List<E> petites = etapes.stream()
                .filter(e -> valeur.applyAsLong(e) * 100 < total * PART_MINIMALE_POURCENT)
                .toList();
        List<R> resultat = new ArrayList<>();
        for (E e : etapes) {
            if (petites.size() < 2 || !petites.contains(e)) {
                resultat.add(ligne.apply(e));
            }
        }
        if (petites.size() >= 2) {
            resultat.add(autres.apply(petites));
        }
        return List.copyOf(resultat);
    }

    private static <T> long somme(List<T> elements, ToLongFunction<T> valeur) {
        return elements.stream().mapToLong(valeur).sum();
    }

    private static String zone(String zoneDemandee) {
        return zoneDemandee == null || zoneDemandee.isBlank() ? null : zoneDemandee;
    }

    private String nomPerimetre(String zone) {
        return zone == null
                ? ENSEMBLE_DU_TOGO
                : zones.nomZone(zone).orElseThrow(() -> new RessourceIntrouvable("Zone inconnue : " + zone));
    }

    private static void verifierOrdre(LocalDate du, LocalDate au) {
        if (du != null && au != null && du.isAfter(au)) {
            throw new RequeteInvalide("La date « du » doit précéder la date « au ».");
        }
    }
}
