package tg.anid.bi.cartes;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

/**
 * Lecture des agrégats de l'impression des cartes (migration V15) : bi.fait_demande_impression_jour (commandes au jour
 * de réception), bi.fait_carte_jour (cartes au jour d'expédition), bi.fait_delai_carte_jour (histogramme du délai du
 * NIU à la remise) et bi.fait_annulation_impression_jour (annulations par motif). Le périmètre est une zone de
 * bi.zone et toute sa descendance jusqu'aux centres, ou tout le Togo si {@code zone} est null.
 */
@Repository
public class CartesRepository {

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

    /** Filtre de période et de périmètre d'un fait d'alias f (colonnes jour et centre_id). */
    private static final String FILTRE = """
            (cast(:du as date) is null or f.jour >= cast(:du as date))
            and (cast(:au as date) is null or f.jour <= cast(:au as date))
            and (cast(:zone as text) is null or f.centre_id in (select id from perimetre))
            """;

    private final JdbcClient jdbc;

    public CartesRepository(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    /** Commandes par statut sur la période, au jour de réception. */
    public record TotauxDemandes(long demandes, long envoyees, long enAttente, long rejetees, long nonClassees,
                                 long annulees, LocalDate derniereRejetee, long erreursIdps,
                                 LocalDate derniereErreurIdps) {
    }

    /** NIU de première inscription sans commande d'impression (stock), dont ceux de plus de 7 jours. */
    public record NiuSansCommande(long total, long plus7j) {
    }

    /** Cartes expédiées sur la période, remises (par mode) ou à remettre. */
    public record TotauxCartes(long expediees, long remises, long remisesHorsLigne, long remisesEnLigne,
                               long remisesSupport, long remisesAutre, long aRemettre) {
    }

    /** Un centre et ses cartes, avec sa préfecture et sa région. */
    public record Centre(String code, String nom, String prefecture, String region, long remises, long expediees) {
    }

    /** Vrai dès que bi.fait_demande_impression_jour contient au moins une ligne (source alimentée). */
    public boolean disponible() {
        return jdbc.sql("select exists (select 1 from bi.fait_demande_impression_jour)")
                .query(Boolean.class)
                .single();
    }

    public TotauxDemandes demandes(LocalDate du, LocalDate au, String zone) {
        return jdbc.sql(AVEC_PERIMETRE + """
                        select coalesce(sum(f.demandes), 0)     as demandes,
                               coalesce(sum(f.envoyees), 0)     as envoyees,
                               coalesce(sum(f.en_attente), 0)   as en_attente,
                               coalesce(sum(f.rejetees), 0)     as rejetees,
                               coalesce(sum(f.non_classees), 0) as non_classees,
                               coalesce(sum(f.annulees), 0)     as annulees,
                               max(f.jour) filter (where f.rejetees > 0) as derniere_rejetee,
                               coalesce(sum(f.erreurs_idps), 0) as erreurs_idps,
                               max(f.jour) filter (where f.erreurs_idps > 0) as derniere_erreur_idps
                        from bi.fait_demande_impression_jour f
                        where """ + FILTRE)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .query((rs, ligne) -> new TotauxDemandes(
                        rs.getLong("demandes"),
                        rs.getLong("envoyees"),
                        rs.getLong("en_attente"),
                        rs.getLong("rejetees"),
                        rs.getLong("non_classees"),
                        rs.getLong("annulees"),
                        rs.getObject("derniere_rejetee", LocalDate.class),
                        rs.getLong("erreurs_idps"),
                        rs.getObject("derniere_erreur_idps", LocalDate.class)))
                .single();
    }

    public TotauxCartes cartes(LocalDate du, LocalDate au, String zone) {
        return jdbc.sql(AVEC_PERIMETRE + """
                        select coalesce(sum(f.expediees), 0)          as expediees,
                               coalesce(sum(f.remises), 0)            as remises,
                               coalesce(sum(f.remises_hors_ligne), 0) as remises_hors_ligne,
                               coalesce(sum(f.remises_en_ligne), 0)   as remises_en_ligne,
                               coalesce(sum(f.remises_support), 0)    as remises_support,
                               coalesce(sum(f.remises_autre), 0)      as remises_autre,
                               coalesce(sum(f.a_remettre), 0)         as a_remettre
                        from bi.fait_carte_jour f
                        where """ + FILTRE)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .query((rs, ligne) -> new TotauxCartes(
                        rs.getLong("expediees"),
                        rs.getLong("remises"),
                        rs.getLong("remises_hors_ligne"),
                        rs.getLong("remises_en_ligne"),
                        rs.getLong("remises_support"),
                        rs.getLong("remises_autre"),
                        rs.getLong("a_remettre")))
                .single();
    }

    /** NIU de première inscription sans commande d'impression dans le périmètre, au dernier calcul (stock). */
    public NiuSansCommande niuSansCommande(String zone) {
        return jdbc.sql(AVEC_PERIMETRE + """
                        select coalesce(sum(s.niu), 0) as total,
                               coalesce(sum(s.niu) filter (where s.anciennete = 'plus_7j'), 0) as plus_7j
                        from bi.stock_niu_sans_commande s
                        where cast(:zone as text) is null or s.centre_id in (select id from perimetre)
                        """)
                .param("zone", zone)
                .query((rs, ligne) -> new NiuSansCommande(rs.getLong("total"), rs.getLong("plus_7j")))
                .single();
    }

    /**
     * Délai médian du NIU à la remise, en jours, sur les cartes expédiées sur la période : la plus petite classe de
     * bi.fait_delai_carte_jour où le cumul atteint la moitié des cartes (exacte au jour près sous 90 jours). Vide sans
     * carte remise.
     */
    public Optional<Integer> delaiMedianJours(LocalDate du, LocalDate au, String zone) {
        return jdbc.sql(AVEC_PERIMETRE + """
                        , histo as (
                            select f.classe_j, sum(f.cartes) as n
                            from bi.fait_delai_carte_jour f
                            where """ + FILTRE + """
                            group by f.classe_j
                        ),
                        cumul as (
                            select classe_j,
                                   sum(n) over (order by classe_j) as cumule,
                                   sum(n) over () as total
                            from histo
                        )
                        select mediane
                        from (select min(classe_j) as mediane from cumul where 2 * cumule >= total) m
                        where mediane is not null
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .query(Integer.class)
                .optional();
    }

    /**
     * Jour de la dernière donnée d'impression : celui de la pastille « Dernière mise à jour » (bi.source_fraicheur,
     * source cartes, heure du Togo), à défaut le dernier jour de commande. Vide s'il n'y a encore aucune donnée.
     */
    public Optional<LocalDate> derniereDonnee() {
        return jdbc.sql("""
                        select jour
                        from (select coalesce(
                                         (select cast(derniere_donnee at time zone 'Africa/Lome' as date)
                                          from bi.source_fraicheur
                                          where source = 'cartes'),
                                         (select max(jour) from bi.fait_demande_impression_jour)) as jour) as d
                        where jour is not null
                        """)
                .query(LocalDate.class)
                .optional();
    }

    /**
     * Demandes, rejetées et annulées par semaine de réception (clé : lundi ; valeurs dans cet ordre), du lundi
     * {@code debut} au dimanche {@code fin}.
     */
    public Map<LocalDate, long[]> demandesParSemaine(LocalDate debut, LocalDate fin, String zone) {
        return jdbc.sql(AVEC_PERIMETRE + """
                        select cast(date_trunc('week', cast(f.jour as timestamp)) as date) as lundi,
                               sum(f.demandes) as demandes, sum(f.rejetees) as rejetees,
                               sum(f.annulees) as annulees
                        from bi.fait_demande_impression_jour f
                        where f.jour between cast(:debut as date) and cast(:fin as date)
                          and (cast(:zone as text) is null or f.centre_id in (select id from perimetre))
                        group by 1
                        """)
                .param("debut", debut)
                .param("fin", fin)
                .param("zone", zone)
                .query((rs, ligne) -> Map.entry(rs.getObject("lundi", LocalDate.class),
                        new long[] {rs.getLong("demandes"), rs.getLong("rejetees"), rs.getLong("annulees")}))
                .list()
                .stream()
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    /** Cartes expédiées par semaine d'expédition (clé : lundi), du lundi {@code debut} au dimanche {@code fin}. */
    public Map<LocalDate, Long> expedieesParSemaine(LocalDate debut, LocalDate fin, String zone) {
        return jdbc.sql(AVEC_PERIMETRE + """
                        select cast(date_trunc('week', cast(f.jour as timestamp)) as date) as lundi,
                               sum(f.expediees) as expediees
                        from bi.fait_carte_jour f
                        where f.jour between cast(:debut as date) and cast(:fin as date)
                          and (cast(:zone as text) is null or f.centre_id in (select id from perimetre))
                        group by 1
                        """)
                .param("debut", debut)
                .param("fin", fin)
                .param("zone", zone)
                .query((rs, ligne) -> Map.entry(rs.getObject("lundi", LocalDate.class), rs.getLong("expediees")))
                .list()
                .stream()
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    /**
     * Une ligne par sous-zone directe de {@code zone} (les régions si {@code zone} est null), cartes cumulées sur toute
     * sa descendance. La zone « hors référentiel » n'apparaît que si elle a des cartes.
     */
    public List<TerritoireCartes.LigneZone> sousZones(LocalDate du, LocalDate au, String zone) {
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
                        faits as (
                            select f.centre_id,
                                   sum(f.expediees)  as expediees,
                                   sum(f.remises)    as remises,
                                   sum(f.a_remettre) as a_remettre
                            from bi.fait_carte_jour f
                            where (cast(:du as date) is null or f.jour >= cast(:du as date))
                              and (cast(:au as date) is null or f.jour <= cast(:au as date))
                            group by f.centre_id
                        )
                        select e.code, e.nom, e.niveau, e.ouvrable,
                               coalesce(sum(f.expediees), 0)  as expediees,
                               coalesce(sum(f.remises), 0)    as remises,
                               coalesce(sum(f.a_remettre), 0) as a_remettre
                        from enfants e
                        join descendance d on d.enfant_id = e.id
                        left join faits f on f.centre_id = d.zone_id
                        group by e.code, e.nom, e.niveau, e.ordre, e.ouvrable
                        having e.code <> cast(:horsReferentiel as text) or coalesce(sum(f.expediees), 0) > 0
                        order by e.ordre, e.nom
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .param("horsReferentiel", ZONE_HORS_REFERENTIEL)
                .query((rs, ligne) -> {
                    boolean hors = ZONE_HORS_REFERENTIEL.equals(rs.getString("code"));
                    return new TerritoireCartes.LigneZone(
                            rs.getString("code"),
                            rs.getString("nom"),
                            rs.getString("niveau"),
                            hors,
                            rs.getBoolean("ouvrable") && !hors,
                            rs.getLong("expediees"),
                            rs.getLong("remises"),
                            rs.getLong("a_remettre"));
                })
                .list();
    }

    /**
     * Cartes à remettre par tranche d'ancienneté au jour {@code jourCalcul} : moins_30j, 30_90j, 90_180j, plus_180j
     * (jours écoulés depuis l'expédition). Une tranche sans carte n'a pas de clé.
     */
    public Map<String, Long> aRemettreParAnciennete(LocalDate du, LocalDate au, String zone, LocalDate jourCalcul) {
        return jdbc.sql(AVEC_PERIMETRE + """
                        select case
                                   when cast(:calcul as date) - f.jour < 30  then 'moins_30j'
                                   when cast(:calcul as date) - f.jour < 90  then '30_90j'
                                   when cast(:calcul as date) - f.jour < 180 then '90_180j'
                                   else 'plus_180j'
                               end as tranche,
                               sum(f.a_remettre) as cartes
                        from bi.fait_carte_jour f
                        where f.a_remettre > 0 and """ + FILTRE + """
                        group by 1
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .param("calcul", jourCalcul)
                .query((rs, ligne) -> Map.entry(rs.getString("tranche"), rs.getLong("cartes")))
                .list()
                .stream()
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    /** Les {@code limite} centres du périmètre qui ont remis le plus de cartes expédiées sur la période. */
    public List<Centre> topCentres(LocalDate du, LocalDate au, String zone, int limite) {
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
                            select f.centre_id, sum(f.remises) as remises, sum(f.expediees) as expediees
                            from bi.fait_carte_jour f
                            where """ + FILTRE + """
                            group by f.centre_id
                        )
                        select z.code, z.nom, c.prefecture, c.region, v.remises, v.expediees
                        from valeurs v
                        join bi.zone z on z.id = v.centre_id
                        join chemin c on c.id = v.centre_id
                        where v.remises > 0
                        order by v.remises desc, z.nom
                        limit :limite
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .param("limite", limite)
                .query((rs, ligne) -> new Centre(
                        rs.getString("code"),
                        rs.getString("nom"),
                        rs.getString("prefecture"),
                        rs.getString("region"),
                        rs.getLong("remises"),
                        rs.getLong("expediees")))
                .list();
    }

    /** Ventilations dans le temps de l'Exploration : format to_char de la clé (année, mois). */
    static final Map<String, String> VENTILATIONS_TEMPS = Map.of("annee", "YYYY", "mois", "YYYY-MM");

    /**
     * Lignes de l'Exploration par année ou par mois ({@link #VENTILATIONS_TEMPS}), dans l'ordre du temps : demandes au
     * mois de réception, cartes au mois d'expédition. Une période sans demande ni carte n'a pas de ligne.
     */
    public List<ExplorationCartes.Ligne> lignesParTemps(LocalDate du, LocalDate au, String zone, String par) {
        String format = VENTILATIONS_TEMPS.get(par);
        if (format == null) {
            throw new IllegalArgumentException("Ventilation inconnue : " + par);
        }
        return jdbc.sql(AVEC_PERIMETRE + """
                        , d as (
                            select to_char(f.jour, cast(:format as text)) as cle, sum(f.demandes) as demandes
                            from bi.fait_demande_impression_jour f
                            where """ + FILTRE + """
                            group by 1
                        ),
                        c as (
                            select to_char(f.jour, cast(:format as text)) as cle, sum(f.expediees) as expediees,
                                   sum(f.remises) as remises, sum(f.a_remettre) as a_remettre
                            from bi.fait_carte_jour f
                            where """ + FILTRE + """
                            group by 1
                        )
                        select coalesce(d.cle, c.cle) as cle,
                               coalesce(d.demandes, 0)   as demandes,
                               coalesce(c.expediees, 0)  as expediees,
                               coalesce(c.remises, 0)    as remises,
                               coalesce(c.a_remettre, 0) as a_remettre
                        from d full join c on c.cle = d.cle
                        order by 1
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .param("format", format)
                .query((rs, ligne) -> new ExplorationCartes.Ligne(rs.getString("cle"), rs.getString("cle"), null,
                        false, false, new ExplorationCartes.Chiffres(rs.getLong("demandes"), rs.getLong("expediees"),
                                rs.getLong("remises"), rs.getLong("a_remettre"))))
                .list();
    }

    /**
     * Lignes de l'Exploration par sous-zone directe de {@code zone} (les régions si {@code zone} est null), chiffres
     * cumulés sur toute sa descendance, dans l'ordre du référentiel. La zone « hors référentiel » n'apparaît que si
     * elle a des demandes ou des cartes.
     */
    public List<ExplorationCartes.Ligne> lignesParSousZone(LocalDate du, LocalDate au, String zone) {
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
                        fd as (
                            select f.centre_id, sum(f.demandes) as demandes
                            from bi.fait_demande_impression_jour f
                            where (cast(:du as date) is null or f.jour >= cast(:du as date))
                              and (cast(:au as date) is null or f.jour <= cast(:au as date))
                            group by f.centre_id
                        ),
                        fc as (
                            select f.centre_id, sum(f.expediees) as expediees, sum(f.remises) as remises,
                                   sum(f.a_remettre) as a_remettre
                            from bi.fait_carte_jour f
                            where (cast(:du as date) is null or f.jour >= cast(:du as date))
                              and (cast(:au as date) is null or f.jour <= cast(:au as date))
                            group by f.centre_id
                        )
                        select e.code, e.nom, e.niveau, e.ouvrable,
                               coalesce(sum(fd.demandes), 0)   as demandes,
                               coalesce(sum(fc.expediees), 0)  as expediees,
                               coalesce(sum(fc.remises), 0)    as remises,
                               coalesce(sum(fc.a_remettre), 0) as a_remettre
                        from enfants e
                        join descendance d on d.enfant_id = e.id
                        left join fd on fd.centre_id = d.zone_id
                        left join fc on fc.centre_id = d.zone_id
                        group by e.code, e.nom, e.niveau, e.ordre, e.ouvrable
                        having e.code <> cast(:horsReferentiel as text)
                            or coalesce(sum(fd.demandes), 0) + coalesce(sum(fc.expediees), 0) > 0
                        order by e.ordre, e.nom
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .param("horsReferentiel", ZONE_HORS_REFERENTIEL)
                .query((rs, ligne) -> {
                    boolean hors = ZONE_HORS_REFERENTIEL.equals(rs.getString("code"));
                    return new ExplorationCartes.Ligne(
                            rs.getString("code"),
                            rs.getString("nom"),
                            rs.getString("niveau"),
                            hors,
                            rs.getBoolean("ouvrable") && !hors,
                            new ExplorationCartes.Chiffres(rs.getLong("demandes"), rs.getLong("expediees"),
                                    rs.getLong("remises"), rs.getLong("a_remettre")));
                })
                .list();
    }

    /** Commandes annulées par motif sur la période (jour de réception), de la plus fréquente à la moins fréquente. */
    public List<AnnulationsParMotif.Motif> annulationsParMotif(LocalDate du, LocalDate au, String zone) {
        return jdbc.sql(AVEC_PERIMETRE + """
                        select f.motif, min(f.motif_libelle) as libelle, sum(f.demandes) as demandes
                        from bi.fait_annulation_impression_jour f
                        where """ + FILTRE + """
                        group by f.motif
                        order by 3 desc, 2
                        """)
                .param("du", du)
                .param("au", au)
                .param("zone", zone)
                .query((rs, ligne) -> new AnnulationsParMotif.Motif(
                        rs.getString("motif"),
                        rs.getString("libelle"),
                        rs.getLong("demandes")))
                .list();
    }
}
