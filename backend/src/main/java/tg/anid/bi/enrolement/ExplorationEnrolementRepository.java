package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

/**
 * Lecture de l'onglet Enrôlement de l'Exploration : bi.fait_enrolement_jour (inscriptions par jour de réception, centre,
 * type de demande, sexe, tranche d'âge et nationalité, V18) et bi.fait_preinscription_zone_jour (pré-inscriptions par
 * jour de création et préfecture).
 * Attention aux blocs de texte : Java retire les espaces de début et de fin de ligne, d'où les fragments qui
 * commencent par une parenthèse (incidents du 05/11/2026).
 */
@Repository
public class ExplorationEnrolementRepository {

    /** Ventilations dans le temps : format to_char de la clé. */
    static final Map<String, String> VENTILATIONS_TEMPS = Map.of("annee", "YYYY", "mois", "YYYY-MM");

    /** Ventilations par une colonne du fait : colonne, puis ordre des lignes (liste blanche, jamais du texte reçu). */
    static final Map<String, String[]> VENTILATIONS_COLONNE = Map.of(
            "type", new String[] {"f.type_demande", "inscriptions desc, cle"},
            "sexe", new String[] {"f.sexe", "array_position(array['F', 'H', 'I'], cle)"},
            "age", new String[] {"f.tranche_age", "array_position(array['0-5', '6-14', '15-18', '19-25', '26-35', "
                    + "'36-45', '46-60', '60+', 'inconnu'], cle)"},
            "nationalite", new String[] {"f.nationalite", "inscriptions desc, cle"});

    /** Filtres de l'onglet ; null : pas de filtre. */
    public record Filtres(String type, String sexe, String age, String nationalite) {

        static final Filtres AUCUN = new Filtres(null, null, null, null);

        boolean profil() {
            return sexe != null || age != null || nationalite != null;
        }
    }

    /** La zone :zone et toutes ses sous-zones jusqu'aux centres (aucune ligne si :zone est null). */
    private static final String AVEC_PERIMETRE = """
            with recursive perimetre as (
                select id from bi.zone where code = cast(:zone as text)
                union all
                select z.id from bi.zone z join perimetre p on z.parent_id = p.id
            )
            """;

    /** Filtres de profil des inscriptions (alias f) : type de demande, sexe, tranche d'âge, nationalité. */
    private static final String FILTRE_PROFIL = """
            (cast(:type as text) is null or f.type_demande = cast(:type as text))
            and (cast(:sexe as text) is null or f.sexe = cast(:sexe as text))
            and (cast(:age as text) is null or f.tranche_age = cast(:age as text))
            and (cast(:nationalite as text) is null or f.nationalite = cast(:nationalite as text))
            """;

    /** Filtre des inscriptions (alias f) : période, profil, zone. */
    private static final String FILTRE_INSCRIPTIONS = """
            (cast(:du as date) is null or f.jour >= cast(:du as date))
            and (cast(:au as date) is null or f.jour <= cast(:au as date))
            and (cast(:zone as text) is null or f.centre_id in (select id from perimetre))
            and""" + "\n" + FILTRE_PROFIL;

    /** Filtre des pré-inscriptions (alias p) : période, zone. */
    private static final String FILTRE_PREINSCRIPTIONS = """
            (cast(:du as date) is null or p.jour >= cast(:du as date))
            and (cast(:au as date) is null or p.jour <= cast(:au as date))
            and (cast(:zone as text) is null or p.zone_id in (select id from perimetre))
            """;

    private static final String SOMMES = """
            coalesce(sum(f.inscriptions), 0) as inscriptions,
            coalesce(sum(f.niu_generes), 0)  as niu_generes,
            coalesce(sum(f.en_cours), 0)     as en_cours,
            coalesce(sum(f.echouees), 0)     as echouees,
            coalesce(sum(f.rejetees), 0)     as rejetees
            """;

    private final JdbcClient jdbc;

    public ExplorationEnrolementRepository(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    /** Totaux de la zone (pré-inscriptions comprises, toujours lues : le service les retire si un type est filtré). */
    public ExplorationEnrolement.Chiffres total(LocalDate du, LocalDate au, String zone, Filtres filtres) {
        return jdbc.sql(AVEC_PERIMETRE + "select\n" + SOMMES + """
                        , (select coalesce(sum(p.demandes), 0) from bi.fait_preinscription_zone_jour p
                           where""" + "\n" + FILTRE_PREINSCRIPTIONS + """
                          ) as preinscriptions
                        from bi.fait_enrolement_jour f
                        where""" + "\n" + FILTRE_INSCRIPTIONS)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .param("type", filtres.type())
                .param("sexe", filtres.sexe())
                .param("age", filtres.age())
                .param("nationalite", filtres.nationalite())
                .query((rs, ligne) -> chiffres(rs.getLong("inscriptions"), rs.getLong("niu_generes"),
                        rs.getLong("en_cours"), rs.getLong("echouees"), rs.getLong("rejetees"),
                        rs.getLong("preinscriptions")))
                .single();
    }

    /** Lignes par année ou par mois ({@link #VENTILATIONS_TEMPS}), dans l'ordre du temps. */
    public List<ExplorationEnrolement.Ligne> lignesParTemps(LocalDate du, LocalDate au, String zone, Filtres filtres,
                                                            String par) {
        String format = VENTILATIONS_TEMPS.get(par);
        if (format == null) {
            throw new IllegalArgumentException("Ventilation inconnue : " + par);
        }
        return jdbc.sql(AVEC_PERIMETRE + """
                        , i as (
                            select to_char(f.jour, cast(:format as text)) as cle,
                        """ + SOMMES + """
                            from bi.fait_enrolement_jour f
                            where""" + "\n" + FILTRE_INSCRIPTIONS + """
                            group by 1
                        ),
                        p as (
                            select to_char(p.jour, cast(:format as text)) as cle, sum(p.demandes) as demandes
                            from bi.fait_preinscription_zone_jour p
                            where""" + "\n" + FILTRE_PREINSCRIPTIONS + """
                            group by 1
                        )
                        select coalesce(i.cle, p.cle) as cle,
                               coalesce(i.inscriptions, 0) as inscriptions, coalesce(i.niu_generes, 0) as niu_generes,
                               coalesce(i.en_cours, 0) as en_cours, coalesce(i.echouees, 0) as echouees,
                               coalesce(i.rejetees, 0) as rejetees, coalesce(p.demandes, 0) as preinscriptions
                        from i full join p on p.cle = i.cle
                        order by 1
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .param("type", filtres.type())
                .param("sexe", filtres.sexe())
                .param("age", filtres.age())
                .param("nationalite", filtres.nationalite())
                .param("format", format)
                .query((rs, ligne) -> new ExplorationEnrolement.Ligne(rs.getString("cle"), rs.getString("cle"), null,
                        false, false, chiffres(rs.getLong("inscriptions"), rs.getLong("niu_generes"),
                        rs.getLong("en_cours"), rs.getLong("echouees"), rs.getLong("rejetees"),
                        rs.getLong("preinscriptions"))))
                .list();
    }

    /**
     * Lignes par type de demande, sexe, tranche d'âge ou nationalité ({@link #VENTILATIONS_COLONNE}) ; pas de
     * pré-inscriptions (une pré-inscription n'a ni type de demande, ni profil par centre).
     */
    public List<ExplorationEnrolement.Ligne> lignesParColonne(LocalDate du, LocalDate au, String zone, Filtres filtres,
                                                              String par) {
        String[] ventilation = VENTILATIONS_COLONNE.get(par);
        if (ventilation == null) {
            throw new IllegalArgumentException("Ventilation inconnue : " + par);
        }
        return avec(jdbc.sql(AVEC_PERIMETRE + "select * from (select " + ventilation[0] + " as cle,\n" + SOMMES + """
                        from bi.fait_enrolement_jour f
                        where""" + "\n" + FILTRE_INSCRIPTIONS + """
                        group by 1
                        ) l
                        order by\s""" + ventilation[1]), du, au, zone, filtres)
                .query((rs, ligne) -> new ExplorationEnrolement.Ligne(rs.getString("cle"), rs.getString("cle"), null,
                        false, false, chiffres(rs.getLong("inscriptions"), rs.getLong("niu_generes"),
                        rs.getLong("en_cours"), rs.getLong("echouees"), rs.getLong("rejetees"), null)))
                .list();
    }

    /**
     * Lignes par sous-zone directe de {@code zone} (les régions si null), chiffres cumulés sur toute sa descendance,
     * dans l'ordre du référentiel ; « hors référentiel » seulement s'il a des inscriptions ou des pré-inscriptions.
     */
    public List<ExplorationEnrolement.Ligne> lignesParSousZone(LocalDate du, LocalDate au, String zone,
                                                               Filtres filtres) {
        return jdbc.sql("""
                        with recursive
                        enfants as (
                            select z.id, z.code, z.nom, z.niveau, z.ordre,
                                   exists (select 1 from bi.zone c where c.parent_id = z.id) as ouvrable
                            from bi.zone z
                            where (cast(:zone as text) is null and z.parent_id is null)
                               or z.parent_id = (select r.id from bi.zone r where r.code = cast(:zone as text))
                        ),
                        descendance as (
                            select e.id as enfant_id, e.id as zone_id from enfants e
                            union all
                            select d.enfant_id, z.id from bi.zone z join descendance d on z.parent_id = d.zone_id
                        ),
                        prefaits as (
                            select p.zone_id, sum(p.demandes) as demandes
                            from bi.fait_preinscription_zone_jour p
                            where (cast(:du as date) is null or p.jour >= cast(:du as date))
                              and (cast(:au as date) is null or p.jour <= cast(:au as date))
                            group by p.zone_id
                        ),
                        faits as (
                            select f.centre_id, sum(f.inscriptions) as inscriptions, sum(f.niu_generes) as niu_generes,
                                   sum(f.en_cours) as en_cours, sum(f.echouees) as echouees,
                                   sum(f.rejetees) as rejetees
                            from bi.fait_enrolement_jour f
                            where (cast(:du as date) is null or f.jour >= cast(:du as date))
                              and (cast(:au as date) is null or f.jour <= cast(:au as date))
                              and""" + "\n" + FILTRE_PROFIL + """
                            group by f.centre_id
                        )
                        select e.code, e.nom, e.niveau, e.ouvrable,
                               coalesce(sum(f.inscriptions), 0) as inscriptions,
                               coalesce(sum(f.niu_generes), 0)  as niu_generes,
                               coalesce(sum(f.en_cours), 0)     as en_cours,
                               coalesce(sum(f.echouees), 0)     as echouees,
                               coalesce(sum(f.rejetees), 0)     as rejetees,
                               coalesce(sum(p.demandes), 0)     as preinscriptions
                        from enfants e
                        join descendance d on d.enfant_id = e.id
                        left join faits f on f.centre_id = d.zone_id
                        left join prefaits p on p.zone_id = d.zone_id
                        group by e.code, e.nom, e.niveau, e.ordre, e.ouvrable
                        having e.code <> cast(:horsReferentiel as text)
                            or coalesce(sum(f.inscriptions), 0) > 0
                            or coalesce(sum(p.demandes), 0) > 0
                        order by e.ordre, e.nom
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .param("type", filtres.type())
                .param("sexe", filtres.sexe())
                .param("age", filtres.age())
                .param("nationalite", filtres.nationalite())
                .param("horsReferentiel", EnrolementRepository.ZONE_HORS_REFERENTIEL)
                .query((rs, ligne) -> {
                    boolean hors = EnrolementRepository.ZONE_HORS_REFERENTIEL.equals(rs.getString("code"));
                    return new ExplorationEnrolement.Ligne(rs.getString("code"), rs.getString("nom"),
                            rs.getString("niveau"), hors, rs.getBoolean("ouvrable") && !hors,
                            chiffres(rs.getLong("inscriptions"), rs.getLong("niu_generes"), rs.getLong("en_cours"),
                                    rs.getLong("echouees"), rs.getLong("rejetees"), rs.getLong("preinscriptions")));
                })
                .list();
    }

    /** Types de demande MOSIP présents dans les inscriptions publiées. */
    public List<String> types() {
        return jdbc.sql("select distinct f.type_demande from bi.fait_enrolement_jour f order by 1")
                .query(String.class)
                .list();
    }

    /** Nationalités présentes dans les inscriptions publiées, de la plus fréquente à la moins fréquente. */
    public List<String> nationalites() {
        return jdbc.sql("""
                        select f.nationalite
                        from bi.fait_enrolement_jour f
                        group by 1
                        order by sum(f.inscriptions) desc, 1
                        """)
                .query(String.class)
                .list();
    }

    private static JdbcClient.StatementSpec avec(JdbcClient.StatementSpec requete, LocalDate du, LocalDate au,
                                                 String zone, Filtres filtres) {
        return requete
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .param("type", filtres.type())
                .param("sexe", filtres.sexe())
                .param("age", filtres.age())
                .param("nationalite", filtres.nationalite());
    }

    private static ExplorationEnrolement.Chiffres chiffres(long inscriptions, long niu, long enCours, long echouees,
                                                           long rejetees, Long preinscriptions) {
        return new ExplorationEnrolement.Chiffres(inscriptions, niu, enCours, echouees, rejetees, preinscriptions);
    }
}
