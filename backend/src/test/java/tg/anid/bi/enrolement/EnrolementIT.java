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

/**
 * Chaîne Data Mart → API sur un PostgreSQL jetable (Testcontainers) : migrations V1 et V2, données de démonstration,
 * état courant écrit comme le ferait le job Spark, recalcul des faits par la fonction SQL, puis lecture par l'API.
 */
@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:tc:postgresql:17-alpine:///bi",
        "spring.datasource.driver-class-name=org.testcontainers.jdbc.ContainerDatabaseDriver",
        "spring.datasource.username=test",
        "spring.datasource.password=test",
        "spring.flyway.locations=classpath:db/migration,classpath:db/dev",
        "bi.securite.active=false"
})
class EnrolementIT {

    @Autowired
    EnrolementService service;

    @Autowired
    JdbcClient jdbc;

    @BeforeEach
    void preparer() {
        jdbc.sql("truncate etat.registration, bi.fait_enrolement_jour").update();
        // Quatre inscriptions (empreintes fictives) : Savanes 1, Savanes 1, Kara 1, centre absent du référentiel.
        jdbc.sql("""
                insert into etat.registration (rid_empreinte, code_centre, reg_type, status_code, cr_dtimes, _lsn)
                values ('e1', '10011', 'NEW', 'PROCESSED',  '2026-10-15 09:00', 1),
                       ('e2', '10011', 'NEW', 'PROCESSING', '2026-10-15 10:00', 2),
                       ('e3', '10021', 'NEW', 'REJECTED',   '2026-10-15 11:00', 3),
                       ('e4', '99999', 'NEW', 'FAILED',     '2026-10-14 12:00', 4)
                """).update();
        jdbc.sql("select count(*) from (select bi.recalculer_enrolement_tout()) as recalcul")
                .query(Long.class)
                .single();
    }

    @AfterEach
    void nettoyer() {
        SecurityContextHolder.clearContext();
    }

    @Test
    void ensembleDuTogoSurToutesLesDates() {
        DevenirInscriptions d = service.devenir(null, null, null);

        assertThat(d.perimetre()).isEqualTo("Ensemble du Togo");
        assertThat(d.inscriptions()).isEqualTo(4);
        assertThat(d.niuGeneres()).isEqualTo(1);
        assertThat(d.enCours()).isEqualTo(1);
        assertThat(d.rejetees()).isEqualTo(1);
        assertThat(d.echouees()).isEqualTo(1);
        assertThat(d.nonClassees()).isZero();
        assertThat(d.niuGeneres() + d.enCours() + d.echouees() + d.rejetees() + d.nonClassees())
                .isEqualTo(d.inscriptions());
    }

    @Test
    void periodeEtZone() {
        LocalDate jour = LocalDate.parse("2026-10-15");
        assertThat(service.devenir(jour, jour, null).inscriptions()).isEqualTo(3);

        DevenirInscriptions savanes = service.devenir(null, null, "SAV");
        assertThat(savanes.perimetre()).isEqualTo("Savanes");
        assertThat(savanes.inscriptions()).isEqualTo(2);

        // Le centre absent du référentiel reste visible, jamais perdu.
        assertThat(service.devenir(null, null, "HORS_REFERENTIEL").echouees()).isEqualTo(1);
    }

    @Test
    void unUtilisateurRegionalNeVoitQueSaRegion() {
        Jwt jeton = Jwt.withTokenValue("jeton").header("alg", "none").claim("zone", "KAR").build();
        SecurityContextHolder.getContext().setAuthentication(
                new JwtAuthenticationToken(jeton, List.of(new SimpleGrantedAuthority("ROLE_BI_REGIONAL"))));

        DevenirInscriptions kara = service.devenir(null, null, null);
        assertThat(kara.perimetre()).isEqualTo("Kara");
        assertThat(kara.inscriptions()).isEqualTo(1);
        assertThatThrownBy(() -> service.devenir(null, null, "SAV")).isInstanceOf(AccessDeniedException.class);
    }
}
