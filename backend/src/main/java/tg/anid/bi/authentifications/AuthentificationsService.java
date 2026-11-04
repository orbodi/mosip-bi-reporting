package tg.anid.bi.authentifications;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.springframework.stereotype.Service;

import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.enrolement.EnrolementService;

/**
 * Page Authentifications (docs/indicateurs.md, section Authentifications ; décisions des 03 et 04/11/2026). Deux
 * périmètres jamais additionnés : les usagers (partenaires, portail du résident, USSD) en tête de page, les
 * vérifications biométriques du traitement des paquets dans un bloc à part. Lecture au jour d'enregistrement de
 * l'authentification ; pas de territoire (toujours « Ensemble du Togo »).
 */
@Service
public class AuthentificationsService {

    static final String ENSEMBLE_DU_TOGO = "Ensemble du Togo";
    static final int NOMBRE_SEMAINES = 12;
    /** Types d'authentification dans l'ordre du tableau. */
    static final List<String> TYPES = List.of("biometrique", "otp", "demographique", "combinee", "sans_mode",
            "non_classe");
    static final String CANAL_PARTENAIRE = "partenaire";

    private final AuthentificationsRepository repository;

    public AuthentificationsService(AuthentificationsRepository repository) {
        this.repository = repository;
    }

    /** Bloc des usagers : requêtes par statut et par type, partenaires raccordés, demandes et codes OTP. */
    public RequetesUsagers usagers(LocalDate du, LocalDate au) {
        verifierOrdre(du, au);
        if (!repository.disponible()) {
            return RequetesUsagers.nonDisponible(ENSEMBLE_DU_TOGO, du, au);
        }
        AuthentificationsRepository.Totaux t = repository.totaux(AuthentificationsRepository.USAGERS, du, au);
        AuthentificationsRepository.Otp o = repository.otp(du, au);
        List<AuthentificationsRepository.Appelant> partenaires = repository.appelants(du, au).stream()
                .filter(a -> CANAL_PARTENAIRE.equals(a.canal()))
                .toList();
        long requetesPartenaires = partenaires.stream().mapToLong(AuthentificationsRepository.Appelant::requetes).sum();
        return new RequetesUsagers(ENSEMBLE_DU_TOGO, du, au, true, t.requetes(), t.reussies(), t.echouees(),
                t.autresStatuts(), t.biometriques(), t.otp(), t.demographiquesEtCombinees(), t.sansMode(),
                t.nonClassees(), (long) partenaires.size(), requetesPartenaires,
                partenaires.stream().map(AuthentificationsRepository.Appelant::nom).toList(), o.demandes(),
                o.demandes() - o.refusees(), o.codes(), o.utilises());
    }

    /** Requêtes et échecs des usagers par type, dans l'ordre fixe du tableau, y compris les types à 0. */
    public TypesAuthentification types(LocalDate du, LocalDate au) {
        verifierOrdre(du, au);
        Map<String, long[]> parType = repository.parType(du, au);
        long[] aucun = {0, 0};
        List<TypesAuthentification.Type> types = TYPES.stream()
                .map(code -> {
                    long[] v = parType.getOrDefault(code, aucun);
                    return new TypesAuthentification.Type(code, v[0], v[1]);
                })
                .toList();
        return new TypesAuthentification(du, au, types);
    }

    /** Échecs par motif des usagers ({@code perimetre} usagers, par défaut) ou du traitement des paquets. */
    public CausesEchec causes(String perimetre, LocalDate du, LocalDate au) {
        verifierOrdre(du, au);
        String p = perimetre == null || perimetre.isBlank() ? AuthentificationsRepository.USAGERS : perimetre;
        if (!AuthentificationsRepository.USAGERS.equals(p) && !AuthentificationsRepository.PAQUETS.equals(p)) {
            throw new RequeteInvalide("Le périmètre vaut « usagers » ou « paquets ».");
        }
        List<CausesEchec.Motif> motifs = repository.causes(p, du, au);
        long echecs = motifs.stream().mapToLong(CausesEchec.Motif::echecs).sum();
        return new CausesEchec(p, du, au, echecs, motifs);
    }

    /** Partenaires, portail du résident et USSD, du plus actif au moins actif (sans leur code MOSIP). */
    public PartenairesEtCanaux partenaires(LocalDate du, LocalDate au) {
        verifierOrdre(du, au);
        List<PartenairesEtCanaux.Appelant> appelants = repository.appelants(du, au).stream()
                .map(a -> new PartenairesEtCanaux.Appelant(a.canal(), a.nom(), a.requetes(), a.reussies(),
                        a.demandesOtp(), a.derniereRequete()))
                .toList();
        long raccordes = appelants.stream().filter(a -> CANAL_PARTENAIRE.equals(a.canal())).count();
        return new PartenairesEtCanaux(du, au, raccordes, appelants);
    }

    /**
     * Requêtes réussies et échouées des usagers des 12 semaines complètes qui finissent au plus tard à la fin de la
     * période (ou à la dernière donnée d'authentification).
     */
    public AuthentificationsParSemaine semaines(LocalDate du, LocalDate au) {
        verifierOrdre(du, au);
        Optional<LocalDate> derniere = repository.derniereDonnee();
        if (derniere.isEmpty()) {
            return new AuthentificationsParSemaine(du, au, List.of());
        }
        LocalDate fin = au == null || au.isAfter(derniere.get()) ? derniere.get() : au;
        List<LocalDate> lundis = EnrolementService.lundisDesSemainesCompletes(fin, NOMBRE_SEMAINES);
        Map<LocalDate, long[]> valeurs = repository.usagersParSemaine(lundis.getFirst(), lundis.getLast().plusDays(6));
        long[] aucune = {0, 0};
        List<AuthentificationsParSemaine.Semaine> semaines = lundis.stream()
                .map(lundi -> {
                    long[] v = valeurs.getOrDefault(lundi, aucune);
                    return new AuthentificationsParSemaine.Semaine(lundi,
                            EnrolementService.touchePeriode(lundi, du, au), v[0], v[1]);
                })
                .toList();
        return new AuthentificationsParSemaine(du, au, semaines);
    }

    /** Bloc du traitement des paquets : vérifications biométriques faites par MOSIP, réussies et échouées. */
    public VerificationsPaquets paquets(LocalDate du, LocalDate au) {
        verifierOrdre(du, au);
        if (!repository.disponible()) {
            return new VerificationsPaquets(du, au, false, null, null, null, null);
        }
        AuthentificationsRepository.Totaux t = repository.totaux(AuthentificationsRepository.PAQUETS, du, au);
        return new VerificationsPaquets(du, au, true, t.requetes(), t.reussies(), t.echouees(), t.autresStatuts());
    }

    private static void verifierOrdre(LocalDate du, LocalDate au) {
        if (du != null && au != null && du.isAfter(au)) {
            throw new RequeteInvalide("La date « du » doit précéder la date « au ».");
        }
    }
}
