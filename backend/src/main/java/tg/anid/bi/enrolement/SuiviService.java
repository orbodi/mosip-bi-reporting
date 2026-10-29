package tg.anid.bi.enrolement;

import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.time.Clock;
import java.time.Duration;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.regex.Pattern;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;

import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.commun.RessourceIntrouvable;
import tg.anid.bi.commun.ServiceIndisponible;
import tg.anid.bi.config.BiProprietes;

/**
 * Suivi d'un dossier : l'empreinte du RID est calculée en mémoire, hmac(rid, clé, 'sha256') comme à la publication
 * de bi.suivi_dossier (pgcrypto, clé SUIVI_HMAC_CLE), puis cherchée. Le RID n'est ni gardé, ni renvoyé, ni écrit
 * dans un journal ou un message d'erreur. Chaque recherche est journalisée (qui, quand, résultat), sans plafond
 * (décision du 26/10/2026) ; chaque utilisateur a accès à tout le Togo (décision du 25/10/2026).
 */
@Service
public class SuiviService {

    static final Pattern FORMAT_RID = Pattern.compile("\\d{29}");
    static final Duration SEUIL_BLOQUE = Duration.ofDays(30);
    static final String INTROUVABLE = "Ce RID ne correspond à aucun dossier ou paquet.";

    private final SuiviRepository repository;
    private final EnrolementRepository zones;
    private final String cle;
    private final Clock horloge;

    @Autowired
    public SuiviService(SuiviRepository repository, EnrolementRepository zones, BiProprietes proprietes) {
        this(repository, zones, proprietes.suivi().cle(), Clock.systemUTC());
    }

    SuiviService(SuiviRepository repository, EnrolementRepository zones, String cle, Clock horloge) {
        this.repository = repository;
        this.zones = zones;
        this.cle = cle;
        this.horloge = horloge;
    }

    /** Le dossier du RID ; 400 si le RID n'a pas 29 chiffres, 404 s'il n'est pas connu, 503 sans clé configurée. */
    public SuiviDossier suivre(String rid) {
        if (cle == null || cle.isBlank()) {
            throw new ServiceIndisponible("Le suivi d'un dossier n'est pas configuré sur ce serveur.");
        }
        String utilisateur = utilisateurCourant();
        if (rid == null || !FORMAT_RID.matcher(rid).matches()) {
            repository.journaliser(utilisateur, "format");
            throw new RequeteInvalide("Le RID compte 29 chiffres.");
        }
        SuiviRepository.Ligne l = repository.parEmpreinte(empreinte(rid, cle)).orElse(null);
        repository.journaliser(utilisateur, l == null ? "introuvable" : "trouve");
        if (l == null) {
            throw new RessourceIntrouvable(INTROUVABLE);
        }
        List<Territoire.ZoneParente> ascendants = zones.ascendants(l.centreCode());
        String region = ascendants.stream().filter(z -> "region".equals(z.niveau())).map(Territoire.ZoneParente::nom)
                .findFirst().orElse(null);
        String prefecture = ascendants.stream().filter(z -> "prefecture".equals(z.niveau()))
                .map(Territoire.ZoneParente::nom).findFirst().orElse(null);
        boolean bloque = "en_cours".equals(l.devenir()) && l.derniereTransactionLe() != null
                && l.derniereTransactionLe().isBefore(OffsetDateTime.now(horloge).minus(SEUIL_BLOQUE));
        SuiviDossier.Etape etape = l.etape() == null ? null
                : new SuiviDossier.Etape(l.etape(), l.etapeLibelle() == null ? l.etape() : l.etapeLibelle(),
                        l.etapeStatut());
        SuiviDossier.Motif motif = l.motif() == null ? null
                : new SuiviDossier.Motif(l.motif(), l.motifLibelle() == null ? l.motif() : l.motifLibelle(),
                        l.motifCommentaire());
        return new SuiviDossier(l.typeDemande(), l.devenir(), bloque,
                new SuiviDossier.Centre(l.centreNom(), prefecture, region), etape, motif, l.derniereTransactionLe(),
                new SuiviDossier.Jalons(l.enroleLe(), l.synchroniseLe(), l.refusPoste(), l.recuLe(), l.niuLe()),
                l.majLe());
    }

    /** hmac(rid, clé, 'sha256') de pgcrypto : clé et RID en UTF-8, HMAC-SHA256. */
    static byte[] empreinte(String rid, String cle) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(cle.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            return mac.doFinal(rid.getBytes(StandardCharsets.UTF_8));
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException("HMAC-SHA256 indisponible", e);
        }
    }

    /** Identifiant Keycloak de l'utilisateur (preferred_username, sinon sub) ; « anonyme » sans Keycloak. */
    static String utilisateurCourant() {
        Authentication a = SecurityContextHolder.getContext().getAuthentication();
        if (a != null && a.getPrincipal() instanceof Jwt jeton) {
            String nom = jeton.getClaimAsString("preferred_username");
            return nom != null && !nom.isBlank() ? nom : jeton.getSubject();
        }
        return "anonyme";
    }
}
