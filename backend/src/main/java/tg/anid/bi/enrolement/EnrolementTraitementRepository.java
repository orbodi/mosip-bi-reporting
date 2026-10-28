package tg.anid.bi.enrolement;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

/**
 * Lecture des tables des migrations V7 et V9 (étapes d'arrêt, motifs, paquets en cours, délais, synchronisés non
 * reçus), pour une zone et toute sa descendance jusqu'aux centres, ou tout le Togo si {@code zone} est null.
 */
@Repository
public class EnrolementTraitementRepository {

    private static final String PERIMETRE = """
            with recursive perimetre as (
                select id from bi.zone where code = cast(:zone as text)
                union all
                select z.id from bi.zone z join perimetre p on z.parent_id = p.id
            )
            """;

    private final JdbcClient jdbc;

    public EnrolementTraitementRepository(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    /** Paquets arrêtés à une étape (devenir rejete ou echoue), étapes dans l'ordre du traitement. */
    public record ArretEtape(String devenir, String etape, String libelle, int ordre, long inscriptions) {
    }

    /** Paquets en cours à une étape, dont bloqués (ancienneté plus_30j). */
    public record EnCoursEtape(String etape, String libelle, int ordre, long inscriptions, long bloques) {
    }

    /** Paquets d'un devenir (rejete, echoue, en_cours) à une étape et un motif ; bloqués pour les en cours. */
    public record Motif(String devenir, String stage, String stageLibelle, int stageOrdre, String motif,
                        String motifLibelle, String motifCommentaire, String motifPiste, long inscriptions,
                        long bloques) {
    }

    /** Une classe d'histogramme de délai : borne basse en heures, paquets. */
    public record Classe(int classeH, long paquets) {
    }

    /** Stock de synchronisés non reçus de la zone. */
    public record StockSynchro(long nonRecus, long plusDe7Jours, OffsetDateTime plusAncienneLe,
                               OffsetDateTime calculeLe) {
    }

    /** Rejets et échecs par étape d'arrêt, au jour de réception (bornes incluses, null = non bornée). */
    public List<ArretEtape> arretsParEtape(LocalDate du, LocalDate au, String zone) {
        return jdbc.sql(PERIMETRE + """
                        select f.devenir, f.etape, min(f.etape_libelle) as libelle, min(f.etape_ordre) as ordre,
                               sum(f.inscriptions) as inscriptions
                        from bi.fait_arret_etape_jour f
                        where (cast(:du as date) is null or f.jour >= cast(:du as date))
                          and (cast(:au as date) is null or f.jour <= cast(:au as date))
                          and (cast(:zone as text) is null or f.centre_id in (select id from perimetre))
                        group by f.devenir, f.etape
                        having sum(f.inscriptions) > 0
                        order by ordre, f.etape
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .query((rs, ligne) -> new ArretEtape(rs.getString("devenir"), rs.getString("etape"),
                        rs.getString("libelle"), rs.getInt("ordre"), rs.getLong("inscriptions")))
                .list();
    }

    /** Paquets en cours par étape, à l'heure du dernier calcul du stock. */
    public List<EnCoursEtape> enCoursParEtape(String zone) {
        return jdbc.sql(PERIMETRE + """
                        select s.etape, min(s.etape_libelle) as libelle, min(s.etape_ordre) as ordre,
                               sum(s.inscriptions) as inscriptions,
                               coalesce(sum(s.inscriptions) filter (where s.anciennete = 'plus_30j'), 0) as bloques
                        from bi.stock_en_cours s
                        where cast(:zone as text) is null or s.centre_id in (select id from perimetre)
                        group by s.etape
                        having sum(s.inscriptions) > 0
                        order by ordre, s.etape
                        """)
                .param("zone", zone)
                .query((rs, ligne) -> new EnCoursEtape(rs.getString("etape"), rs.getString("libelle"),
                        rs.getInt("ordre"), rs.getLong("inscriptions"), rs.getLong("bloques")))
                .list();
    }

    /**
     * Rejets et échecs par étape et motif, au jour de réception (bornes incluses, null = non bornée), puis paquets en
     * cours par étape et motif (stock, sans période), du plus fréquent au moins fréquent dans chaque devenir.
     */
    public List<Motif> parMotif(LocalDate du, LocalDate au, String zone) {
        return jdbc.sql(PERIMETRE + """
                        select devenir, stage, stage_libelle, stage_ordre, motif, motif_libelle, motif_commentaire,
                               motif_piste, inscriptions, bloques
                        from (
                            select f.devenir, f.stage, min(f.stage_libelle) as stage_libelle,
                                   min(f.stage_ordre) as stage_ordre, f.motif, min(f.motif_libelle) as motif_libelle,
                                   min(f.motif_commentaire) as motif_commentaire, min(f.motif_piste) as motif_piste,
                                   sum(f.inscriptions) as inscriptions, 0 as bloques
                            from bi.fait_arret_motif_jour f
                            where (cast(:du as date) is null or f.jour >= cast(:du as date))
                              and (cast(:au as date) is null or f.jour <= cast(:au as date))
                              and (cast(:zone as text) is null or f.centre_id in (select id from perimetre))
                            group by f.devenir, f.stage, f.motif
                            union all
                            select 'en_cours', s.stage, min(s.stage_libelle), min(s.stage_ordre), s.motif,
                                   min(s.motif_libelle), min(s.motif_commentaire), min(s.motif_piste),
                                   sum(s.inscriptions),
                                   coalesce(sum(s.inscriptions) filter (where s.anciennete = 'plus_30j'), 0)
                            from bi.stock_en_cours_motif s
                            where cast(:zone as text) is null or s.centre_id in (select id from perimetre)
                            group by s.stage, s.motif
                        ) m
                        where inscriptions > 0
                        order by devenir, inscriptions desc, stage_ordre, stage, motif
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .query((rs, ligne) -> new Motif(rs.getString("devenir"), rs.getString("stage"),
                        rs.getString("stage_libelle"), rs.getInt("stage_ordre"), rs.getString("motif"),
                        rs.getString("motif_libelle"), rs.getString("motif_commentaire"), rs.getString("motif_piste"),
                        rs.getLong("inscriptions"), rs.getLong("bloques")))
                .list();
    }

    /** Heure du dernier calcul du stock des paquets en cours par motif (null tant que rien n'est publié). */
    public OffsetDateTime enCoursMotifCalculeLe() {
        return jdbc.sql("select max(calcule_le) as calcule_le from bi.stock_en_cours_motif")
                .query((rs, ligne) -> rs.getObject("calcule_le", OffsetDateTime.class))
                .list()
                .getFirst();
    }

    /** Heure du dernier calcul du stock des paquets en cours (null tant que rien n'est publié). */
    public OffsetDateTime enCoursCalculeLe() {
        // Liste d'une ligne (valeur nulle possible) : single() refuserait un résultat nul.
        return jdbc.sql("select max(calcule_le) as calcule_le from bi.stock_en_cours")
                .query((rs, ligne) -> rs.getObject("calcule_le", OffsetDateTime.class))
                .list()
                .getFirst();
    }

    /** Paquets en cours depuis plus de 30 jours (bloqués), dans la zone. */
    public long bloques(String zone) {
        return jdbc.sql(PERIMETRE + """
                        select coalesce(sum(s.inscriptions), 0)
                        from bi.stock_en_cours s
                        where s.anciennete = 'plus_30j'
                          and (cast(:zone as text) is null or s.centre_id in (select id from perimetre))
                        """)
                .param("zone", zone)
                .query(Long.class)
                .single();
    }

    /**
     * Histogramme d'un délai sur la période et la zone : mesure reception_niu (jour du NIU) ou enrolement_reception
     * (jour de réception) ; {@code typeDemande} null = tous les types.
     */
    public List<Classe> histogramme(String mesure, String typeDemande, LocalDate du, LocalDate au, String zone) {
        return jdbc.sql(PERIMETRE + """
                        select f.classe_h, sum(f.paquets) as paquets
                        from bi.fait_delai_jour f
                        where f.mesure = :mesure
                          and (cast(:type as text) is null or f.type_demande = cast(:type as text))
                          and (cast(:du as date) is null or f.jour >= cast(:du as date))
                          and (cast(:au as date) is null or f.jour <= cast(:au as date))
                          and (cast(:zone as text) is null or f.centre_id in (select id from perimetre))
                        group by f.classe_h
                        having sum(f.paquets) > 0
                        order by f.classe_h
                        """)
                .param("mesure", mesure)
                .param("type", typeDemande)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .query((rs, ligne) -> new Classe(rs.getInt("classe_h"), rs.getLong("paquets")))
                .list();
    }

    /** Synchronisés non reçus de la zone, à l'heure du dernier calcul du stock. */
    public StockSynchro synchronisationNonRecue(String zone) {
        return jdbc.sql(PERIMETRE + """
                        select coalesce(sum(s.paquets), 0) as non_recus,
                               coalesce(sum(s.paquets) filter (where s.anciennete = 'plus_7j'), 0) as plus_7j,
                               min(s.plus_ancienne_le) as plus_ancienne_le,
                               (select max(calcule_le) from bi.stock_synchro_non_recue) as calcule_le
                        from bi.stock_synchro_non_recue s
                        where cast(:zone as text) is null or s.centre_id in (select id from perimetre)
                        """)
                .param("zone", zone)
                .query((rs, ligne) -> new StockSynchro(rs.getLong("non_recus"), rs.getLong("plus_7j"),
                        rs.getObject("plus_ancienne_le", OffsetDateTime.class),
                        rs.getObject("calcule_le", OffsetDateTime.class)))
                .single();
    }
}
