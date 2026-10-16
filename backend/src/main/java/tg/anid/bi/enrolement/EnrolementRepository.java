package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.util.Optional;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

/** Lecture des agrégats d'enrôlement (bi.fait_enrolement_jour, alimenté par le pipeline temps réel). */
@Repository
public class EnrolementRepository {

    private final JdbcClient jdbc;

    public EnrolementRepository(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    /** Totaux par statut regroupé. */
    public record Totaux(long inscriptions, long niuGeneres, long enCours, long echouees, long rejetees,
                         long nonClassees) {
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
}
