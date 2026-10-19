package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

/**
 * Lecture des agrégats d'enrôlement : bi.fait_enrolement_jour (pipeline temps réel, lecture cohorte) et
 * bi.fait_niu_jour (NIU au jour de génération, lecture flux).
 */
@Repository
public class EnrolementRepository {

    /** Zone créée par la migration V2 pour les centres absents du référentiel. */
    static final String ZONE_HORS_REFERENTIEL = "HORS_REFERENTIEL";

    /** La zone :zone et toutes ses sous-zones jusqu'aux centres (aucune ligne si :zone est null). */
    private static final String AVEC_PERIMETRE = """
            with recursive perimetre as (
                select id from bi.zone where code = cast(:zone as text)
                union all
                select z.id from bi.zone z join perimetre p on z.parent_id = p.id
            )
            """;

    private final JdbcClient jdbc;

    public EnrolementRepository(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    /** Totaux par statut regroupé. */
    public record Totaux(long inscriptions, long niuGeneres, long enCours, long echouees, long rejetees,
                         long nonClassees) {
    }

    /** Un centre et ses chiffres sur la période, avec sa préfecture et sa région. */
    public record Centre(String code, String nom, String prefecture, String region, long valeur, long inscriptions) {
    }

    /** Nom de la zone (région, préfecture… centre) qui porte ce code. */
    public Optional<String> nomZone(String code) {
        return jdbc.sql("select nom from bi.zone where code = :code")
                .param("code", code)
                .query(String.class)
                .optional();
    }

    /**
     * Totaux sur la période (bornes incluses, null = non bornée) et le périmètre : la zone et toutes ses
     * sous-zones jusqu'aux centres, ou tout le Togo si {@code zone} est null.
     */
    public Totaux devenir(LocalDate du, LocalDate au, String zone) {
        return jdbc.sql("""
                        with recursive perimetre as (
                            select id from bi.zone where code = cast(:zone as text)
                            union all
                            select z.id from bi.zone z join perimetre p on z.parent_id = p.id
                        )
                        select coalesce(sum(f.inscriptions), 0) as inscriptions,
                               coalesce(sum(f.niu_generes), 0)  as niu_generes,
                               coalesce(sum(f.en_cours), 0)     as en_cours,
                               coalesce(sum(f.echouees), 0)     as echouees,
                               coalesce(sum(f.rejetees), 0)     as rejetees,
                               coalesce(sum(f.non_classees), 0) as non_classees
                        from bi.fait_enrolement_jour f
                        where (cast(:du as date) is null or f.jour >= cast(:du as date))
                          and (cast(:au as date) is null or f.jour <= cast(:au as date))
                          and (cast(:zone as text) is null or f.centre_id in (select id from perimetre))
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .query((rs, ligne) -> new Totaux(
                        rs.getLong("inscriptions"),
                        rs.getLong("niu_generes"),
                        rs.getLong("en_cours"),
                        rs.getLong("echouees"),
                        rs.getLong("rejetees"),
                        rs.getLong("non_classees")))
                .single();
    }

    /**
     * Jour de la dernière donnée d'enrôlement : celui de la pastille « Dernière mise à jour » (bi.source_fraicheur,
     * heure du Togo), à défaut le dernier jour présent dans les faits. Vide s'il n'y a encore aucune donnée.
     */
    public Optional<LocalDate> derniereDonnee() {
        return jdbc.sql("""
                        select jour
                        from (select coalesce(
                                         (select cast(derniere_donnee at time zone 'Africa/Lome' as date)
                                          from bi.source_fraicheur
                                          where source = 'enrolement'),
                                         (select max(jour) from bi.fait_enrolement_jour)) as jour) as d
                        where jour is not null
                        """)
                .query(LocalDate.class)
                .optional();
    }

    /** Inscriptions par semaine (clé : lundi), du lundi {@code debut} au dimanche {@code fin}. */
    public Map<LocalDate, Long> inscriptionsParSemaine(LocalDate debut, LocalDate fin, String zone) {
        return parSemaine(AVEC_PERIMETRE + """
                select cast(date_trunc('week', cast(f.jour as timestamp)) as date) as lundi,
                       sum(f.inscriptions) as total
                from bi.fait_enrolement_jour f
                where f.jour between cast(:debut as date) and cast(:fin as date)
                  and (cast(:zone as text) is null or f.centre_id in (select id from perimetre))
                group by 1
                """, debut, fin, zone);
    }

    /** NIU générés par semaine de génération (clé : lundi), du lundi {@code debut} au dimanche {@code fin}. */
    public Map<LocalDate, Long> niuParSemaine(LocalDate debut, LocalDate fin, String zone) {
        return parSemaine(AVEC_PERIMETRE + """
                select cast(date_trunc('week', cast(f.jour as timestamp)) as date) as lundi,
                       sum(f.niu_generes) as total
                from bi.fait_niu_jour f
                where f.jour between cast(:debut as date) and cast(:fin as date)
                  and (cast(:zone as text) is null or f.centre_id in (select id from perimetre))
                group by 1
                """, debut, fin, zone);
    }

    private Map<LocalDate, Long> parSemaine(String sql, LocalDate debut, LocalDate fin, String zone) {
        return jdbc.sql(sql)
                .param("debut", debut)
                .param("fin", fin)
                .param("zone", zone)
                .query((rs, ligne) -> Map.entry(rs.getObject("lundi", LocalDate.class), rs.getLong("total")))
                .list()
                .stream()
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    /** Vrai dès que bi.fait_niu_jour contient au moins une ligne (source alimentée). */
    public boolean niuDisponibles() {
        return jdbc.sql("select exists (select 1 from bi.fait_niu_jour)")
                .query(Boolean.class)
                .single();
    }

    /**
     * Une ligne par sous-zone directe de {@code zone} (les régions si {@code zone} est null), chiffres cumulés sur
     * toute sa descendance. La zone « hors référentiel » n'apparaît que si elle a des inscriptions.
     */
    public List<Territoire.LigneZone> sousZones(LocalDate du, LocalDate au, String zone) {
        return jdbc.sql("""
                        with recursive
                        enfants as (
                            select z.id, z.code, z.nom, z.niveau, z.ordre
                            from bi.zone z
                            where (cast(:zone as text) is null and z.parent_id is null)
                               or z.parent_id = (select r.id from bi.zone r where r.code = cast(:zone as text))
                        ),
                        descendance as (
                            select e.id as enfant_id, e.id as zone_id from enfants e
                            union all
                            select d.enfant_id, z.id from bi.zone z join descendance d on z.parent_id = d.zone_id
                        ),
                        faits as (
                            select f.centre_id,
                                   sum(f.inscriptions) as inscriptions,
                                   sum(f.niu_generes)  as niu_generes,
                                   sum(f.en_cours)     as en_cours,
                                   sum(f.echouees)     as echouees,
                                   sum(f.rejetees)     as rejetees,
                                   sum(f.non_classees) as non_classees
                            from bi.fait_enrolement_jour f
                            where (cast(:du as date) is null or f.jour >= cast(:du as date))
                              and (cast(:au as date) is null or f.jour <= cast(:au as date))
                            group by f.centre_id
                        )
                        select e.code, e.nom, e.niveau,
                               coalesce(sum(f.inscriptions), 0) as inscriptions,
                               coalesce(sum(f.niu_generes), 0)  as niu_generes,
                               coalesce(sum(f.en_cours), 0)     as en_cours,
                               coalesce(sum(f.echouees), 0)     as echouees,
                               coalesce(sum(f.rejetees), 0)     as rejetees,
                               coalesce(sum(f.non_classees), 0) as non_classees
                        from enfants e
                        join descendance d on d.enfant_id = e.id
                        left join faits f on f.centre_id = d.zone_id
                        group by e.code, e.nom, e.niveau, e.ordre
                        having e.code <> cast(:horsReferentiel as text) or coalesce(sum(f.inscriptions), 0) > 0
                        order by e.ordre, e.nom
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .param("horsReferentiel", ZONE_HORS_REFERENTIEL)
                .query((rs, ligne) -> new Territoire.LigneZone(
                        rs.getString("code"),
                        rs.getString("nom"),
                        rs.getString("niveau"),
                        ZONE_HORS_REFERENTIEL.equals(rs.getString("code")),
                        rs.getLong("inscriptions"),
                        rs.getLong("niu_generes"),
                        rs.getLong("en_cours"),
                        rs.getLong("echouees"),
                        rs.getLong("rejetees"),
                        rs.getLong("non_classees")))
                .list();
    }

    /**
     * Les {@code limite} premiers centres du périmètre selon le classement (inscriptions, echecs ou rejets), à valeur
     * égale par ordre alphabétique ; les centres dont la valeur est nulle sont exclus.
     */
    public List<Centre> topCentres(LocalDate du, LocalDate au, String zone, String classement, int limite) {
        return jdbc.sql(AVEC_PERIMETRE + """
                        , chemin as (
                            select id, nom as region, cast(null as text) as prefecture
                            from bi.zone
                            where parent_id is null
                            union all
                            select z.id, c.region, case when z.niveau = 'prefecture' then z.nom else c.prefecture end
                            from bi.zone z join chemin c on z.parent_id = c.id
                        ),
                        valeurs as (
                            select f.centre_id,
                                   sum(f.inscriptions) as inscriptions,
                                   sum(f.echouees)     as echouees,
                                   sum(f.rejetees)     as rejetees
                            from bi.fait_enrolement_jour f
                            where (cast(:du as date) is null or f.jour >= cast(:du as date))
                              and (cast(:au as date) is null or f.jour <= cast(:au as date))
                              and (cast(:zone as text) is null or f.centre_id in (select id from perimetre))
                            group by f.centre_id
                        ),
                        classes as (
                            select v.centre_id, v.inscriptions,
                                   case cast(:classement as text)
                                       when 'echecs' then v.echouees
                                       when 'rejets' then v.rejetees
                                       else v.inscriptions
                                   end as valeur
                            from valeurs v
                        )
                        select z.code, z.nom, c.prefecture, c.region, k.valeur, k.inscriptions
                        from classes k
                        join bi.zone z on z.id = k.centre_id
                        join chemin c on c.id = k.centre_id
                        where k.valeur > 0
                        order by k.valeur desc, z.nom
                        limit :limite
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .param("classement", classement)
                .param("limite", limite)
                .query((rs, ligne) -> new Centre(
                        rs.getString("code"),
                        rs.getString("nom"),
                        rs.getString("prefecture"),
                        rs.getString("region"),
                        rs.getLong("valeur"),
                        rs.getLong("inscriptions")))
                .list();
    }
}
