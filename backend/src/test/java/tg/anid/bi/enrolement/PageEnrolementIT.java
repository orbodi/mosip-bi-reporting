package tg.anid.bi.enrolement;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.LocalDate;
import java.util.List;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;

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

    @AfterEach
    void nettoyer() {
        SecurityContextHolder.clearContext();
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

    @Test
    void unUtilisateurRegionalNeVoitQueSaRegionDansChaqueBloc() {
        Jwt jeton = Jwt.withTokenValue("jeton").header("alg", "none").claim("zone", "KAR").build();
        SecurityContextHolder.getContext().setAuthentication(
                new JwtAuthenticationToken(jeton, List.of(new SimpleGrantedAuthority("ROLE_BI_REGIONAL"))));

        assertThat(regions.regions()).extracting(Region::code).containsExactly("KAR");

        Territoire t = service.territoire(null, null, null);
        assertThat(t.perimetre()).isEqualTo("Kara");
        assertThat(t.inscriptions()).isEqualTo(80);
        assertThat(t.lignes()).allSatisfy(l -> assertThat(l.niveau()).isEqualTo("prefecture"));

        assertThat(service.centres(null, null, null, "inscriptions").centres())
                .extracting(TopCentres.CentreClasse::code).containsExactly("10021");
        InscriptionsParSemaine s = service.semaines(null, null, null);
        assertThat(s.perimetre()).isEqualTo("Kara");
        assertThat(s.semaines().getLast().inscriptions()).isEqualTo(80);
        assertThat(s.semaines().getLast().niuGeneres()).isEqualTo(50);

        LocalDate jour = LocalDate.parse("2026-01-05");
        assertThatThrownBy(() -> service.territoire(jour, jour, "SAV")).isInstanceOf(AccessDeniedException.class);
        assertThatThrownBy(() -> service.semaines(null, null, "SAV")).isInstanceOf(AccessDeniedException.class);
        assertThatThrownBy(() -> service.centres(null, null, "SAV", "rejets"))
                .isInstanceOf(AccessDeniedException.class);
    }
}
