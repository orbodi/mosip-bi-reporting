package tg.anid.bi.enrolement;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.LocalDate;
import java.time.OffsetDateTime;
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

import tg.anid.bi.commun.RequeteInvalide;

/**
 * Blocs Pré-inscription et NIU par âge et par sexe sur un PostgreSQL jetable (Testcontainers) : migrations V1 à V4,
 * référentiel de développement, faits écrits directement (les jobs du pipeline ont leurs propres tests). Dernière
 * pré-inscription du référentiel de développement : 14/01/2026 à 11h28.
 */
@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:tc:postgresql:17-alpine:///bi",
        "spring.datasource.driver-class-name=org.testcontainers.jdbc.ContainerDatabaseDriver",
        "spring.datasource.username=test",
        "spring.datasource.password=test",
        "spring.flyway.locations=classpath:db/migration,classpath:db/dev",
        "bi.securite.active=false"
})
class PreinscriptionsEtProfilIT {

    @Autowired
    EnrolementService service;

    @Autowired
    JdbcClient jdbc;

    @BeforeEach
    void preparer() {
        jdbc.sql("""
                truncate bi.fait_preinscription_jour, bi.fait_niu_profil_jour, bi.fait_preinscription_profil_jour,
                         bi.fait_preinscription_zone_jour
                """).update();
        jdbc.sql("""
                insert into bi.fait_preinscription_jour (jour, statut, demandes, consommees)
                values (date '2026-01-05', 'reservee', 90, 70),
                       (date '2026-01-05', 'en_attente', 8, 0),
                       (date '2026-01-06', 'reservee', 40, 10),
                       (date '2026-01-06', 'non_classe', 2, 0),
                       (date '2025-12-20', 'expiree', 5, 0)
                """).update();
        jdbc.sql("""
                insert into bi.fait_niu_profil_jour (jour, zone_id, sexe, tranche_age, niu_generes)
                select v.jour, z.id, v.sexe, v.tranche, v.niu
                from (values (date '2026-01-05', 'SAV', 'F', '26-35', 30),
                             (date '2026-01-05', 'SAV', 'H', '26-35', 25),
                             (date '2026-01-06', 'KAR', 'F', '0-5', 4),
                             (date '2026-01-06', 'KAR', 'I', '19-25', 2),
                             (date '2026-01-06', 'HORS_REFERENTIEL', 'H', '60+', 1))
                     as v (jour, code, sexe, tranche, niu)
                join bi.zone z on z.code = v.code
                """).update();
    }

    @AfterEach
    void nettoyer() {
        SecurityContextHolder.clearContext();
    }

    @Test
    void preinscriptionsParStatutEtControleDeLaSomme() {
        Preinscriptions p = service.preinscriptions(null, null);

        assertThat(p.disponible()).isTrue();
        assertThat(p.demandes()).isEqualTo(145);
        assertThat(p.rendezVousReserves()).isEqualTo(130);
        assertThat(p.enAttenteRendezVous()).isEqualTo(8);
        assertThat(p.expirees()).isEqualTo(5);
        assertThat(p.nonClassees()).isEqualTo(2);
        assertThat(p.honorees()).isEqualTo(80);
        assertThat(p.rendezVousReserves() + p.enAttenteRendezVous() + p.expirees() + p.annulees()
                + p.nonClassees()).isEqualTo(p.demandes());
        assertThat(p.derniereDemande()).isEqualTo(OffsetDateTime.parse("2026-01-14T11:28:00Z"));
        assertThat(p.femmes()).isNull();
    }

    @Test
    void sexeDesPreinscriptionsConnuOuInconnu() {
        jdbc.sql("""
                insert into bi.fait_preinscription_jour (jour, statut, sexe, demandes, consommees)
                values (date '2026-01-07', 'reservee', 'F', 12, 0),
                       (date '2026-01-07', 'reservee', 'H', 9, 0),
                       (date '2026-01-07', 'en_attente', 'F', 3, 0)
                """).update();

        Preinscriptions p = service.preinscriptions(null, null);

        assertThat(p.demandes()).isEqualTo(169);
        assertThat(p.femmes()).isEqualTo(15);
        assertThat(p.hommes()).isEqualTo(9);
        assertThat(p.rendezVousReserves() + p.enAttenteRendezVous() + p.expirees() + p.annulees()
                + p.nonClassees()).isEqualTo(p.demandes());
    }

    @Test
    void profilDesPreinscritsParTrancheSexeEtNationalite() {
        jdbc.sql("""
                insert into bi.fait_preinscription_profil_jour (jour, sexe, tranche_age, nationalite, demandes)
                values (date '2026-01-05', 'F', '26-35', 'TOGO', 60),
                       (date '2026-01-05', 'H', '26-35', 'TOGO', 30),
                       (date '2026-01-06', 'H', '19-25', 'BENIN', 5),
                       (date '2026-01-06', 'F', 'inconnu', 'TOGO', 3),
                       (date '2026-01-06', 'I', 'inconnu', 'Non renseignée', 7)
                """).update();

        ProfilPreinscriptions p = service.profilPreinscriptions(null, null);

        assertThat(p.disponible()).isTrue();
        assertThat(p.nonRenseignes()).isEqualTo(7);
        assertThat(p.nationalites()).extracting(ProfilPreinscriptions.Nationalite::nom)
                .containsExactly("TOGO", "BENIN", "Non renseignée");
        assertThat(p.tranches().getLast().femmes()).isEqualTo(3);
        long total = p.tranches().stream().mapToLong(t -> t.femmes() + t.hommes()).sum() + p.nonRenseignes();
        assertThat(total).isEqualTo(105);

        LocalDate jour = LocalDate.parse("2026-01-05");
        assertThat(service.profilPreinscriptions(jour, jour).nationalites()).singleElement()
                .satisfies(n -> assertThat(n.demandes()).isEqualTo(90));
    }

    @Test
    void preinscriptionsDuTerritoireSelonLaPrefectureDeResidence() {
        jdbc.sql("""
                insert into bi.fait_preinscription_zone_jour (jour, zone_id, demandes)
                select v.jour, z.id, v.demandes
                from (values (date '2026-01-05', 'SAV-01', 12),
                             (date '2026-01-06', 'SAV-02', 8),
                             (date '2026-01-06', 'KAR-05', 5))
                     as v (jour, code, demandes)
                join bi.zone z on z.code = v.code
                """).update();

        Territoire togo = service.territoire(null, null, null);
        assertThat(togo.preinscriptions()).isEqualTo(25);
        assertThat(togo.lignes()).filteredOn(l -> l.code().equals("SAV")).singleElement()
                .satisfies(l -> assertThat(l.preinscriptions()).isEqualTo(20));
        assertThat(togo.lignes().stream().mapToLong(Territoire.LigneZone::preinscriptions).sum())
                .isEqualTo(togo.preinscriptions());

        Territoire savanes = service.territoire(null, null, "SAV");
        assertThat(savanes.preinscriptions()).isEqualTo(20);
        assertThat(savanes.lignes()).filteredOn(l -> l.code().equals("SAV-01")).singleElement()
                .satisfies(l -> assertThat(l.preinscriptions()).isEqualTo(12));
    }

    @Test
    void preinscriptionsSurUnePeriode() {
        LocalDate jour = LocalDate.parse("2026-01-05");

        Preinscriptions p = service.preinscriptions(jour, jour);

        assertThat(p.demandes()).isEqualTo(98);
        assertThat(p.honorees()).isEqualTo(70);
    }

    @Test
    void pyramideNationaleEtParRegion() {
        AgeSexe togo = service.ageSexe(null, null, null);
        assertThat(togo.tranches()).hasSize(8);
        assertThat(togo.tranches().get(4).femmes()).isEqualTo(30);
        assertThat(togo.tranches().get(7).hommes()).isEqualTo(1);
        assertThat(togo.nonRenseignes()).isEqualTo(2);
        long total = togo.tranches().stream().mapToLong(t -> t.femmes() + t.hommes()).sum();
        assertThat(total + togo.nonRenseignes()).isEqualTo(62);

        AgeSexe savanes = service.ageSexe(null, null, "SAV");
        assertThat(savanes.perimetre()).isEqualTo("Savanes");
        assertThat(savanes.tranches().get(4).hommes()).isEqualTo(25);
        assertThat(savanes.tranches().getFirst().femmes()).isZero();

        assertThatThrownBy(() -> service.ageSexe(null, null, "SAV-02")).isInstanceOf(RequeteInvalide.class);
    }

    @Test
    void unUtilisateurRegionalNeVoitQueSaRegion() {
        Jwt jeton = Jwt.withTokenValue("jeton").header("alg", "none").claim("zone", "KAR").build();
        SecurityContextHolder.getContext().setAuthentication(
                new JwtAuthenticationToken(jeton, List.of(new SimpleGrantedAuthority("ROLE_BI_REGIONAL"))));

        AgeSexe kara = service.ageSexe(null, null, null);
        assertThat(kara.perimetre()).isEqualTo("Kara");
        assertThat(kara.tranches().getFirst().femmes()).isEqualTo(4);
        assertThat(kara.nonRenseignes()).isEqualTo(2);
        assertThatThrownBy(() -> service.ageSexe(null, null, "SAV")).isInstanceOf(AccessDeniedException.class);

        Preinscriptions p = service.preinscriptions(null, null);
        assertThat(p.perimetre()).isEqualTo("Kara");
        assertThat(p.demandes()).isNull();
    }
}
