package tg.anid.bi.enrolement;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.LocalDate;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.simple.JdbcClient;

import tg.anid.bi.meta.Region;
import tg.anid.bi.meta.RegionsController;

/**
 * Blocs Territoire, Inscriptions et NIU par semaine, Top des centres et filtre Région sur un PostgreSQL jetable
 * (Testcontainers) : migrations V1 à V3, référentiel de développement (régions, préfectures, centres), faits écrits
 * directement (les NIU par jour de génération n'ont pas encore de job). Dernière donnée d'enrôlement du référentiel
 * de développement : mercredi 14/01/2026, donc dernière semaine complète du 05/01 au 11/01/2026.
 */
@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:tc:postgresql:17-alpine:///bi",
        "spring.datasource.driver-class-name=org.testcontainers.jdbc.ContainerDatabaseDriver",
        "spring.datasource.username=test",
        "spring.datasource.password=test",
        "spring.flyway.locations=classpath:db/migration,classpath:db/dev",
        "bi.securite.active=false"
})
class PageEnrolementIT {

    @Autowired
    EnrolementService service;

    @Autowired
    RegionsController regions;

    @Autowired
    JdbcClient jdbc;

    @BeforeEach
    void preparer() {
        jdbc.sql("truncate bi.fait_enrolement_jour, bi.fait_niu_jour, bi.fait_delai_jour").update();
        // Centres du référentiel de dev : 10011 (Tône, Savanes), 10012 (Cinkassé, Savanes), 10021 (Kozah, Kara).
        jdbc.sql("""
                insert into bi.fait_enrolement_jour (jour, centre_id, sexe, tranche_age, type_demande, inscriptions,
                                                     niu_generes, en_cours, echouees, rejetees, non_classees)
                select v.jour, z.id, 'I', 'inconnu', 'NEW', v.ins, v.niu, v.cours, v.ech, v.rej, 0
                from (values (date '2026-01-05', '10011', 100, 90, 4, 1, 5),
                             (date '2026-01-06', '10012',  50, 40, 5, 0, 5),
                             (date '2026-01-07', '10021',  80, 76, 2, 1, 1),
                             (date '2025-12-29', 'CENTRE_NON_REFERENCE', 10, 0, 0, 10, 0))
                     as v (jour, code, ins, niu, cours, ech, rej)
                join bi.zone z on z.code = v.code
                """).update();
        // Le NIU du 12/01 tombe dans la semaine en cours : jamais compté dans les semaines complètes.
        jdbc.sql("""
                insert into bi.fait_niu_jour (jour, centre_id, type_demande, niu_generes)
                select v.jour, z.id, 'NEW', v.niu
                from (values (date '2026-01-08', '10011', 60),
                             (date '2026-01-09', '10021', 50),
                             (date '2026-01-12', '10011', 30))
                     as v (jour, code, niu)
                join bi.zone z on z.code = v.code
                """).update();
    }


    @Test
    void territoireNationalUneLigneParRegionEtLeHorsReferentielQuandIlADesInscriptions() {
        Territoire t = service.territoire(null, null, null);
        DevenirInscriptions d = service.devenir(null, null, null);

        assertThat(t.perimetre()).isEqualTo("Ensemble du Togo");
        assertThat(t.lignes()).extracting(Territoire.LigneZone::code)
                .containsExactly("SAV", "KAR", "CEN", "PLA", "MAR", "GLO", "HORS_REFERENTIEL");
        assertThat(t.lignes().getFirst().inscriptions()).isEqualTo(150);
        assertThat(t.lignes().getLast().horsReferentiel()).isTrue();
        // Contrôles : lignes = totaux de la zone = bloc « Devenir des inscriptions ».
        assertThat(t.lignes().stream().mapToLong(Territoire.LigneZone::inscriptions).sum()).isEqualTo(240);
        assertThat(t.lignes().stream().mapToLong(Territoire.LigneZone::rejetees).sum()).isEqualTo(t.rejetees());
        assertThat(t.inscriptions()).isEqualTo(d.inscriptions());
        assertThat(t.niuGeneres() + t.enCours() + t.echouees() + t.rejetees() + t.nonClassees())
                .isEqualTo(t.inscriptions());
    }

    @Test
    void territoireDUneRegionUneLigneParPrefecture() {
        Territoire t = service.territoire(null, null, "SAV");

        assertThat(t.perimetre()).isEqualTo("Savanes");
        assertThat(t.inscriptions()).isEqualTo(150);
        assertThat(t.lignes()).hasSize(5).allSatisfy(l -> assertThat(l.niveau()).isEqualTo("prefecture"));
        assertThat(t.lignes()).filteredOn(l -> l.inscriptions() > 0)
                .extracting(Territoire.LigneZone::nom, Territoire.LigneZone::inscriptions)
                .containsExactly(org.assertj.core.groups.Tuple.tuple("Cinkassé", 50L),
                        org.assertj.core.groups.Tuple.tuple("Tône", 100L));
        assertThat(t.lignes().stream().mapToLong(Territoire.LigneZone::inscriptions).sum()).isEqualTo(150);
    }

    @Test
    void territoireATousLesNiveauxJusquAuxCentres() {
        // Sous Tône (SAV-02) : commune → canton → localité → centre 10091, et un centre 10092 rattaché directement au
        // canton (cas réel : 1 centre sur 8 841 le 25/10/2026). Zones ajoutées au référentiel de dev, une fois.
        // Une instruction par zone : le parent doit exister avant l'enfant.
        for (String[] z : new String[][] {
                {"commune", "T-COM", "Commune de test", "SAV-02"},
                {"canton", "T-CAN", "Canton de test", "T-COM"},
                {"localite", "T-LOC", "Localité de test", "T-CAN"},
                {"centre", "10091", "Centre de localité", "T-LOC"},
                {"centre", "10092", "Centre de canton", "T-CAN"}}) {
            jdbc.sql("""
                    insert into bi.zone (niveau, code, nom, parent_id)
                    select :niveau, :code, :nom, p.id from bi.zone p where p.code = :parent
                    on conflict (code) do nothing
                    """)
                    .param("niveau", z[0]).param("code", z[1]).param("nom", z[2]).param("parent", z[3])
                    .update();
        }
        jdbc.sql("""
                insert into bi.fait_enrolement_jour (jour, centre_id, sexe, tranche_age, type_demande, inscriptions,
                                                     niu_generes, en_cours, echouees, rejetees, non_classees)
                select date '2026-01-05', z.id, 'I', 'inconnu', 'NEW', v.ins, v.niu, v.ins - v.niu, 0, 0, 0
                from (values ('10091', 30, 25), ('10092', 12, 10)) as v (code, ins, niu)
                join bi.zone z on z.code = v.code
                """).update();

        Territoire prefecture = service.territoire(null, null, "SAV-02");
        assertThat(prefecture.niveau()).isEqualTo("prefecture");
        assertThat(prefecture.ascendants()).extracting(Territoire.ZoneParente::code).containsExactly("SAV");
        // Tône : 100 (centre 10011, rattaché directement à la préfecture) + 42 sous la commune.
        assertThat(prefecture.inscriptions()).isEqualTo(142);
        assertThat(prefecture.lignes()).filteredOn(l -> l.code().equals("T-COM")).singleElement()
                .satisfies(l -> {
                    assertThat(l.inscriptions()).isEqualTo(42);
                    assertThat(l.ouvrable()).isTrue();
                });

        Territoire canton = service.territoire(null, null, "T-CAN");
        assertThat(canton.niveau()).isEqualTo("canton");
        assertThat(canton.ascendants()).extracting(Territoire.ZoneParente::code)
                .containsExactly("SAV", "SAV-02", "T-COM");
        assertThat(canton.lignes()).extracting(Territoire.LigneZone::code, Territoire.LigneZone::niveau,
                        Territoire.LigneZone::inscriptions, Territoire.LigneZone::ouvrable)
                .containsExactlyInAnyOrder(
                        org.assertj.core.groups.Tuple.tuple("T-LOC", "localite", 30L, true),
                        org.assertj.core.groups.Tuple.tuple("10092", "centre", 12L, false));
        // Contrôles : somme des sous-zones = totaux de la zone = bloc « Devenir » sur la même zone.
        assertThat(canton.lignes().stream().mapToLong(Territoire.LigneZone::inscriptions).sum())
                .isEqualTo(canton.inscriptions()).isEqualTo(42);
        assertThat(canton.inscriptions()).isEqualTo(service.devenir(null, null, "T-CAN").inscriptions());
        assertThat(canton.niuGeneres() + canton.enCours() + canton.echouees() + canton.rejetees()
                + canton.nonClassees()).isEqualTo(canton.inscriptions());

        Territoire localite = service.territoire(null, null, "T-LOC");
        assertThat(localite.ascendants()).extracting(Territoire.ZoneParente::niveau)
                .containsExactly("region", "prefecture", "commune", "canton");
        assertThat(localite.lignes()).singleElement().satisfies(l -> {
            assertThat(l.code()).isEqualTo("10091");
            assertThat(l.niuGeneres()).isEqualTo(25);
            assertThat(l.ouvrable()).isFalse();
        });

        Territoire centre = service.territoire(null, null, "10091");
        assertThat(centre.niveau()).isEqualTo("centre");
        assertThat(centre.inscriptions()).isEqualTo(30);
        assertThat(centre.lignes()).isEmpty();

        Territoire national = service.territoire(null, null, null);
        assertThat(national.niveau()).isNull();
        assertThat(national.ascendants()).isEmpty();
        assertThatThrownBy(() -> service.territoire(null, null, "INCONNUE"))
                .isInstanceOf(tg.anid.bi.commun.RessourceIntrouvable.class);
    }

    @Test
    void delaiMedianDeLaReceptionAuNiuParZoneEnHeures() {
        // Histogrammes (migration V7) : Tône 3 NIU à 2 h, 2 à 10 h ; Cinkassé 1 à 30 h ; Kozah 4 à 5 h. Les
        // renouvellements (UPDATE) et l'autre mesure (enrolement_reception) ne comptent pas.
        jdbc.sql("""
                insert into bi.fait_delai_jour (jour, centre_id, type_demande, mesure, classe_h, paquets)
                select v.jour, z.id, v.type, v.mesure, v.classe, v.n
                from (values (date '2026-01-08', '10011', 'NEW', 'reception_niu', 2, 3),
                             (date '2026-01-08', '10011', 'NEW', 'reception_niu', 10, 2),
                             (date '2026-01-09', '10012', 'NEW', 'reception_niu', 30, 1),
                             (date '2026-01-09', '10021', 'NEW', 'reception_niu', 5, 4),
                             (date '2026-01-09', '10021', 'UPDATE', 'reception_niu', 400, 50),
                             (date '2026-01-09', '10011', 'NEW', 'enrolement_reception', 900, 50))
                     as v (jour, code, type, mesure, classe, n)
                join bi.zone z on z.code = v.code
                """).update();

        Territoire togo = service.territoire(null, null, null);
        // Togo : 10 NIU, classes 2 (3), 5 (4), 10 (2), 30 (1) : la moitié est atteinte à 5 h.
        assertThat(togo.delaiMedianH()).isEqualTo(5);
        assertThat(togo.lignes()).filteredOn(l -> l.code().equals("SAV")).singleElement()
                .extracting(Territoire.LigneZone::delaiMedianH).isEqualTo(2);
        assertThat(togo.lignes()).filteredOn(l -> l.code().equals("KAR")).singleElement()
                .extracting(Territoire.LigneZone::delaiMedianH).isEqualTo(5);
        // Région sans NIU : pas de délai (affiché 0 par le front, jamais estimé).
        assertThat(togo.lignes()).filteredOn(l -> l.code().equals("PLA")).singleElement()
                .extracting(Territoire.LigneZone::delaiMedianH).isNull();

        Territoire savanes = service.territoire(null, null, "SAV");
        assertThat(savanes.delaiMedianH()).isEqualTo(2);
        assertThat(savanes.lignes()).filteredOn(l -> l.nom().equals("Cinkassé")).singleElement()
                .extracting(Territoire.LigneZone::delaiMedianH).isEqualTo(30);
    }

    @Test
    void semainesCompletesInscriptionsAuJourDeReceptionNiuAuJourDeGeneration() {
        InscriptionsParSemaine s = service.semaines(null, null, null);

        assertThat(s.niuDisponibles()).isTrue();
        assertThat(s.semaines()).hasSize(12);
        InscriptionsParSemaine.Semaine derniere = s.semaines().getLast();
        assertThat(derniere.lundi()).isEqualTo("2026-01-05");
        assertThat(derniere.inscriptions()).isEqualTo(230);
        assertThat(derniere.niuGeneres()).isEqualTo(110);
        assertThat(s.semaines().get(10).lundi()).isEqualTo("2025-12-29");
        assertThat(s.semaines().get(10).inscriptions()).isEqualTo(10);
    }

    @Test
    void joursInscriptionsAuJourDeReceptionNiuAuJourDeGenerationJourEnCoursCompris() {
        InscriptionsParJour j = service.jours(LocalDate.parse("2026-01-14"));

        assertThat(j.jours()).hasSize(28);
        assertThat(j.jours().getFirst().jour()).isEqualTo("2025-12-18");
        assertThat(j.jours().getLast().jour()).isEqualTo("2026-01-14");
        assertThat(j.jours()).filteredOn(d -> d.jour().equals(LocalDate.parse("2026-01-05"))).singleElement()
                .extracting(InscriptionsParJour.Jour::inscriptions).isEqualTo(100L);
        // Le NIU du 12/01 compte au jour près, contrairement aux semaines complètes.
        assertThat(j.jours()).filteredOn(d -> d.jour().equals(LocalDate.parse("2026-01-12"))).singleElement()
                .extracting(InscriptionsParJour.Jour::niuGeneres).isEqualTo(30L);
        // Contrôle : les 28 jours couvrent toutes les données du jeu, donc leur somme égale les totaux des faits.
        assertThat(j.jours().stream().mapToLong(InscriptionsParJour.Jour::inscriptions).sum())
                .isEqualTo(jdbc.sql("select sum(inscriptions) from bi.fait_enrolement_jour").query(Long.class).single())
                .isEqualTo(240);
        assertThat(j.jours().stream().mapToLong(InscriptionsParJour.Jour::niuGeneres).sum()).isEqualTo(140);
    }

    @Test
    void sansNiuParJourDeGenerationLaSourceEstSignaleeIndisponible() {
        jdbc.sql("truncate bi.fait_niu_jour").update();

        assertThat(service.semaines(null, null, null).niuDisponibles()).isFalse();
    }

    @Test
    void topDesCentresParInscriptionsEchecsEtRejets() {
        assertThat(service.centres(null, null, null, "inscriptions").centres())
                .extracting(TopCentres.CentreClasse::code)
                .containsExactly("10011", "10021", "10012", "CENTRE_NON_REFERENCE");

        TopCentres echecs = service.centres(null, null, null, "echecs");
        // 10012 n'a aucun échec : absent ; à égalité, ordre alphabétique (Kara 1 avant Savanes 1).
        assertThat(echecs.centres()).extracting(TopCentres.CentreClasse::code)
                .containsExactly("CENTRE_NON_REFERENCE", "10021", "10011");
        assertThat(echecs.centres().getFirst().region()).isEqualTo("Hors référentiel");
        assertThat(echecs.centres().getFirst().prefecture()).isNull();

        TopCentres.CentreClasse premier = service.centres(null, null, "SAV", "rejets").centres().getFirst();
        assertThat(premier.rang()).isEqualTo(1);
        assertThat(premier.prefecture()).isEqualTo("Tône");
        assertThat(premier.region()).isEqualTo("Savanes");
        assertThat(premier.valeur()).isEqualTo(5);
        assertThat(premier.inscriptions()).isEqualTo(100);
    }

    @Test
    void filtreRegionLesSixRegionsDuNordAuSud() {
        assertThat(regions.regions()).extracting(Region::code)
                .containsExactly("SAV", "KAR", "CEN", "PLA", "MAR", "GLO");
    }
}
