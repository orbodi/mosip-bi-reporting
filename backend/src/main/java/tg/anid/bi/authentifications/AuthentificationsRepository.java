package tg.anid.bi.authentifications;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

/**
 * Lecture des agrégats des authentifications (migration V17) : bi.fait_authentification_jour (authentifications par
 * jour, appelant, type, statut et motif), bi.fait_demande_otp_jour (demandes de code OTP), bi.fait_code_otp_jour
 * (codes OTP) et bi.ref_motif_authentification (libellés). Pas de territoire. Les deux périmètres (usagers, paquets)
 * sont toujours lus séparément.
 */
@Repository
public class AuthentificationsRepository {

    static final String USAGERS = "usagers";
    static final String PAQUETS = "paquets";

    /** Filtre de période d'un fait d'alias f (colonne jour). */
    private static final String PERIODE = """
            (cast(:du as date) is null or f.jour >= cast(:du as date))
            and (cast(:au as date) is null or f.jour <= cast(:au as date))
            """;

    private final JdbcClient jdbc;

    public AuthentificationsRepository(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    /** Authentifications d'un périmètre par statut et par type. */
    public record Totaux(long requetes, long reussies, long echouees, long autresStatuts, long biometriques, long otp,
                         long demographiquesEtCombinees, long sansMode, long nonClassees) {
    }

    /** Demandes de code OTP et codes OTP de la période. */
    public record Otp(long demandes, long refusees, long codes, long utilises) {
    }

    /** Un appelant des usagers et son activité sur la période. */
    public record Appelant(String appelantId, String canal, String nom, long requetes, long reussies,
                           long demandesOtp, LocalDate derniereRequete) {
    }

    /** Vrai dès que bi.fait_authentification_jour contient au moins une ligne (source alimentée). */
    public boolean disponible() {
        return jdbc.sql("select exists (select 1 from bi.fait_authentification_jour)")
                .query(Boolean.class)
                .single();
    }

    public Totaux totaux(String perimetre, LocalDate du, LocalDate au) {
        return jdbc.sql("""
                        select coalesce(sum(f.authentifications), 0) as requetes,
                               coalesce(sum(f.authentifications) filter (where f.statut = 'reussie'), 0) as reussies,
                               coalesce(sum(f.authentifications) filter (where f.statut = 'echouee'), 0) as echouees,
                               coalesce(sum(f.authentifications) filter (where f.statut = 'non_classe'), 0) as autres,
                               coalesce(sum(f.authentifications) filter (where f.type = 'biometrique'), 0) as bio,
                               coalesce(sum(f.authentifications) filter (where f.type = 'otp'), 0) as otp,
                               coalesce(sum(f.authentifications)
                                        filter (where f.type in ('demographique', 'combinee')), 0) as demo,
                               coalesce(sum(f.authentifications) filter (where f.type = 'sans_mode'), 0) as sans_mode,
                               coalesce(sum(f.authentifications) filter (where f.type = 'non_classe'), 0) as non_classe
                        from bi.fait_authentification_jour f
                        where f.perimetre = :perimetre and """ + PERIODE)
                .param("perimetre", perimetre)
                .param("du", du)
                .param("au", au)
                .query((rs, ligne) -> new Totaux(rs.getLong("requetes"), rs.getLong("reussies"),
                        rs.getLong("echouees"), rs.getLong("autres"), rs.getLong("bio"), rs.getLong("otp"),
                        rs.getLong("demo"), rs.getLong("sans_mode"), rs.getLong("non_classe")))
                .single();
    }

    /** Demandes de code OTP des usagers et codes OTP (tous appelants : otp_transaction ne dit pas lequel). */
    public Otp otp(LocalDate du, LocalDate au) {
        return jdbc.sql("""
                        select (select coalesce(sum(f.demandes), 0) from bi.fait_demande_otp_jour f
                                where f.perimetre = 'usagers' and """ + PERIODE + """
                               ) as demandes,
                               (select coalesce(sum(f.refusees), 0) from bi.fait_demande_otp_jour f
                                where f.perimetre = 'usagers' and """ + PERIODE + """
                               ) as refusees,
                               (select coalesce(sum(f.codes), 0) from bi.fait_code_otp_jour f where """ + PERIODE + """
                               ) as codes,
                               (select coalesce(sum(f.utilises), 0) from bi.fait_code_otp_jour f where """ + PERIODE + """
                               ) as utilises
                        """)
                .param("du", du)
                .param("au", au)
                .query((rs, ligne) -> new Otp(rs.getLong("demandes"), rs.getLong("refusees"), rs.getLong("codes"),
                        rs.getLong("utilises")))
                .single();
    }

    /** Requêtes et échecs des usagers par type (code du type → {requêtes, échecs}). */
    public Map<String, long[]> parType(LocalDate du, LocalDate au) {
        return jdbc.sql("""
                        select f.type, sum(f.authentifications) as requetes,
                               coalesce(sum(f.authentifications) filter (where f.statut = 'echouee'), 0) as echecs
                        from bi.fait_authentification_jour f
                        where f.perimetre = 'usagers' and """ + PERIODE + """
                        group by f.type
                        """)
                .param("du", du)
                .param("au", au)
                .query((rs, ligne) -> Map.entry(rs.getString("type"),
                        new long[] {rs.getLong("requetes"), rs.getLong("echecs")}))
                .list()
                .stream()
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    /** Échecs d'un périmètre par motif, du plus fréquent au moins fréquent. */
    public List<CausesEchec.Motif> causes(String perimetre, LocalDate du, LocalDate au) {
        return jdbc.sql("""
                        select f.motif, coalesce(r.libelle, 'Motif non répertorié') as libelle,
                               sum(f.authentifications) as echecs
                        from bi.fait_authentification_jour f
                        left join bi.ref_motif_authentification r on r.motif = f.motif
                        where f.perimetre = :perimetre and f.statut = 'echouee' and """ + PERIODE + """
                        group by 1, 2
                        order by 3 desc, 2
                        """)
                .param("perimetre", perimetre)
                .param("du", du)
                .param("au", au)
                .query((rs, ligne) -> new CausesEchec.Motif(rs.getString("motif"), rs.getString("libelle"),
                        rs.getLong("echecs")))
                .list();
    }

    /**
     * Appelants des usagers (authentifications et demandes de code OTP), du plus actif au moins actif ; nom : celui
     * du jour le plus récent.
     */
    public List<Appelant> appelants(LocalDate du, LocalDate au) {
        return jdbc.sql("""
                        with a as (
                            select f.appelant_id, min(f.canal) as canal,
                                   (array_agg(f.appelant order by f.jour desc))[1] as nom,
                                   sum(f.authentifications) as requetes,
                                   coalesce(sum(f.authentifications) filter (where f.statut = 'reussie'), 0) as reussies,
                                   max(f.jour) as derniere
                            from bi.fait_authentification_jour f
                            where f.perimetre = 'usagers' and """ + PERIODE + """
                            group by f.appelant_id
                        ), o as (
                            select f.appelant_id, min(f.canal) as canal,
                                   (array_agg(f.appelant order by f.jour desc))[1] as nom,
                                   sum(f.demandes) as demandes, max(f.jour) as derniere
                            from bi.fait_demande_otp_jour f
                            where f.perimetre = 'usagers' and """ + PERIODE + """
                            group by f.appelant_id
                        )
                        select coalesce(a.appelant_id, o.appelant_id) as appelant_id,
                               coalesce(a.canal, o.canal) as canal, coalesce(a.nom, o.nom) as nom,
                               coalesce(a.requetes, 0) as requetes, coalesce(a.reussies, 0) as reussies,
                               coalesce(o.demandes, 0) as demandes, greatest(a.derniere, o.derniere) as derniere
                        from a full join o on o.appelant_id = a.appelant_id
                        order by 4 desc, 6 desc, 3
                        """)
                .param("du", du)
                .param("au", au)
                .query((rs, ligne) -> new Appelant(rs.getString("appelant_id"), rs.getString("canal"),
                        rs.getString("nom"), rs.getLong("requetes"), rs.getLong("reussies"), rs.getLong("demandes"),
                        rs.getObject("derniere", LocalDate.class)))
                .list();
    }

    /** Ventilations de l'Exploration : expression SQL du regroupement (liste fermée, jamais construite depuis la requête). */
    static final Map<String, String> VENTILATIONS = Map.of(
            "annee", "to_char(f.jour, 'YYYY')",
            "mois", "to_char(f.jour, 'YYYY-MM')",
            "type", "f.type",
            "motif", "f.motif",
            "appelant", "f.appelant");

    /** Filtres de l'Exploration sur un fait d'alias f ; un filtre null n'est pas appliqué. */
    // Commence par une parenthèse, comme PERIODE : Java retire l'espace de fin de « where """ + … » (bloc de texte),
    // et « where(…) » reste du SQL valide.
    private static final String FILTRES_EXPLORATION = """
            (f.perimetre = :perimetre)
            and (cast(:type as text) is null or f.type = cast(:type as text))
            and (cast(:motif as text) is null or f.motif = cast(:motif as text))
            and (cast(:appelant as text) is null or f.appelant = cast(:appelant as text))
            and """ + PERIODE;

    /** Totaux de l'Exploration pour la sélection. */
    public ExplorationAuthentifications.Chiffres totalExploration(String perimetre, LocalDate du, LocalDate au,
                                                                  String type, String motif, String appelant) {
        return jdbc.sql("""
                        select coalesce(sum(f.authentifications), 0) as requetes,
                               coalesce(sum(f.authentifications) filter (where f.statut = 'reussie'), 0) as reussies,
                               coalesce(sum(f.authentifications) filter (where f.statut = 'echouee'), 0) as echouees
                        from bi.fait_authentification_jour f
                        where """ + FILTRES_EXPLORATION)
                .param("perimetre", perimetre)
                .param("du", du)
                .param("au", au)
                .param("type", type)
                .param("motif", motif)
                .param("appelant", appelant)
                .query((rs, ligne) -> new ExplorationAuthentifications.Chiffres(rs.getLong("requetes"),
                        rs.getLong("reussies"), rs.getLong("echouees")))
                .single();
    }

    /**
     * Lignes de l'Exploration pour une ventilation de {@link #VENTILATIONS} : par année et par mois dans l'ordre du
     * temps, sinon de la plus grande à la plus petite. Par motif : seulement les échouées (une réussie n'a pas de motif).
     */
    public List<ExplorationAuthentifications.Ligne> lignesExploration(String perimetre, LocalDate du, LocalDate au,
                                                                      String type, String motif, String appelant,
                                                                      String par) {
        String cle = VENTILATIONS.get(par);
        if (cle == null) {
            throw new IllegalArgumentException("Ventilation inconnue : " + par);
        }
        String ordre = "annee".equals(par) || "mois".equals(par) ? "1" : "3 desc, 1";
        return jdbc.sql("select " + cle + """
                         as cle,
                               coalesce(min(r.libelle), min(""" + cle + """
                        )) as libelle,
                               sum(f.authentifications) as requetes,
                               coalesce(sum(f.authentifications) filter (where f.statut = 'reussie'), 0) as reussies,
                               coalesce(sum(f.authentifications) filter (where f.statut = 'echouee'), 0) as echouees
                        from bi.fait_authentification_jour f
                        left join bi.ref_motif_authentification r
                               on cast(:par as text) = 'motif' and r.motif = f.motif
                        where """ + FILTRES_EXPLORATION + ("motif".equals(par) ? " and f.statut = 'echouee'" : "")
                        + " group by 1 order by " + ordre)
                .param("perimetre", perimetre)
                .param("du", du)
                .param("au", au)
                .param("type", type)
                .param("motif", motif)
                .param("appelant", appelant)
                .param("par", par)
                .query((rs, ligne) -> new ExplorationAuthentifications.Ligne(rs.getString("cle"),
                        rs.getString("libelle"), new ExplorationAuthentifications.Chiffres(rs.getLong("requetes"),
                        rs.getLong("reussies"), rs.getLong("echouees"))))
                .list();
    }

    /** Valeurs des filtres de l'Exploration pour un périmètre, sur toute la durée. */
    public ExplorationAuthentifications.Valeurs valeursExploration(String perimetre) {
        List<String> types = jdbc.sql("""
                        select distinct f.type from bi.fait_authentification_jour f
                        where f.perimetre = :perimetre order by 1
                        """)
                .param("perimetre", perimetre)
                .query(String.class)
                .list();
        List<CausesEchec.Motif> motifs = jdbc.sql("""
                        select f.motif, coalesce(min(r.libelle), 'Motif non répertorié') as libelle,
                               sum(f.authentifications) as echecs
                        from bi.fait_authentification_jour f
                        left join bi.ref_motif_authentification r on r.motif = f.motif
                        where f.perimetre = :perimetre and f.statut = 'echouee'
                        group by 1 order by 3 desc, 2
                        """)
                .param("perimetre", perimetre)
                .query((rs, ligne) -> new CausesEchec.Motif(rs.getString("motif"), rs.getString("libelle"),
                        rs.getLong("echecs")))
                .list();
        List<String> appelants = jdbc.sql("""
                        select f.appelant from bi.fait_authentification_jour f
                        where f.perimetre = :perimetre
                        group by 1 order by sum(f.authentifications) desc, 1
                        """)
                .param("perimetre", perimetre)
                .query(String.class)
                .list();
        return new ExplorationAuthentifications.Valeurs(types, motifs, appelants);
    }

    /**
     * Requêtes réussies et échouées des usagers par semaine (clé : lundi ; valeurs dans cet ordre), du lundi
     * {@code debut} au dimanche {@code fin}.
     */
    public Map<LocalDate, long[]> usagersParSemaine(LocalDate debut, LocalDate fin) {
        return jdbc.sql("""
                        select cast(date_trunc('week', cast(f.jour as timestamp)) as date) as lundi,
                               coalesce(sum(f.authentifications) filter (where f.statut = 'reussie'), 0) as reussies,
                               coalesce(sum(f.authentifications) filter (where f.statut = 'echouee'), 0) as echouees
                        from bi.fait_authentification_jour f
                        where f.perimetre = 'usagers'
                          and f.jour between cast(:debut as date) and cast(:fin as date)
                        group by 1
                        """)
                .param("debut", debut)
                .param("fin", fin)
                .query((rs, ligne) -> Map.entry(rs.getObject("lundi", LocalDate.class),
                        new long[] {rs.getLong("reussies"), rs.getLong("echouees")}))
                .list()
                .stream()
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    /**
     * Jour de la dernière donnée d'authentification : celui de la pastille « Dernière mise à jour »
     * (bi.source_fraicheur, heure du Togo), à défaut le dernier jour des faits.
     */
    public Optional<LocalDate> derniereDonnee() {
        return jdbc.sql("""
                        select jour
                        from (select coalesce(
                                         (select cast(derniere_donnee at time zone 'Africa/Lome' as date)
                                          from bi.source_fraicheur
                                          where source = 'authentifications'),
                                         (select max(jour) from bi.fait_authentification_jour)) as jour) as d
                        where jour is not null
                        """)
                .query(LocalDate.class)
                .optional();
    }
}
