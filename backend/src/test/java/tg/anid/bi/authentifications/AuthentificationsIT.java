package tg.anid.bi.authentifications;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.assertj.core.api.Assertions.tuple;

import java.time.LocalDate;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.jdbc.core.simple.JdbcClient;

/**
 * Page Authentifications sur un PostgreSQL jetable (Testcontainers) : migrations V1 à V17, faits écrits directement
 * comme les publie le pipeline. Dernière donnée d'authentification du référentiel de développement : 14/01/2026 (la
 * pastille), donc dernière semaine complète du 05/01 au 11/01/2026.
 */
@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:tc:postgresql:17-alpine:///bi",
        "spring.datasource.driver-class-name=org.testcontainers.jdbc.ContainerDatabaseDriver",
        "spring.datasource.username=test",
        "spring.datasource.password=test",
        "spring.flyway.locations=classpath:db/migration,classpath:db/dev",
        "bi.securite.active=false"
})
class AuthentificationsIT {

    @Autowired
    AuthentificationsService service;

    @Autowired
    JdbcClient jdbc;

    @BeforeEach
    void preparer() {
        jdbc.sql("""
                truncate bi.fait_authentification_jour, bi.fait_demande_otp_jour, bi.fait_code_otp_jour,
                         bi.ref_motif_authentification
                """).update();
        jdbc.sql("""
                insert into bi.ref_motif_authentification (motif, libelle, ordre) values
                    ('BIO_NON_CONCORDANTE', 'Biométrie non concordante', 70),
                    ('OTP_REFUSE', 'Code OTP ou eKYC refusé', 60),
                    ('SANS_MODE', 'Aucun mode d''authentification demandé', 50),
                    ('AUTRE', 'Motif non répertorié', 999)
                """).update();
        jdbc.sql("""
                insert into bi.fait_authentification_jour (jour, perimetre, canal, appelant_id, appelant, type, statut,
                                                           motif, authentifications) values
                    (date '2026-01-05', 'usagers', 'partenaire', 'AU-ANID', 'Atos', 'otp', 'reussie', 'AUCUN', 30),
                    (date '2026-01-05', 'usagers', 'partenaire', 'AU-ANID', 'Atos', 'otp', 'echouee', 'OTP_REFUSE', 8),
                    (date '2026-01-06', 'usagers', 'partenaire', 'AU-ANID', 'Atos', 'sans_mode', 'echouee', 'SANS_MODE', 4),
                    (date '2026-01-07', 'usagers', 'portail', 'mosip-resident-client', 'Portail du résident', 'otp',
                     'reussie', 'AUCUN', 10),
                    (date '2026-01-07', 'usagers', 'ussd', 'ussd-client', 'USSD', 'biometrique', 'echouee', 'AUTRE', 1),
                    (date '2025-12-29', 'usagers', 'partenaire', 'AU-ANID', 'Atos', 'otp', 'reussie', 'AUCUN', 5),
                    (date '2026-01-05', 'paquets', 'paquets', 'mosip-regproc-client', 'Traitement des paquets',
                     'biometrique', 'reussie', 'AUCUN', 100),
                    (date '2026-01-05', 'paquets', 'paquets', 'mosip-regproc-client', 'Traitement des paquets',
                     'biometrique', 'echouee', 'BIO_NON_CONCORDANTE', 600)
                """).update();
        jdbc.sql("""
                insert into bi.fait_demande_otp_jour (jour, perimetre, canal, appelant_id, appelant, demandes, refusees)
                values (date '2026-01-05', 'usagers', 'partenaire', 'AU-ANID', 'Atos', 50, 6),
                       (date '2026-01-08', 'usagers', 'portail', 'mosip-resident-client', 'Portail du résident', 12, 0)
                """).update();
        jdbc.sql("""
                insert into bi.fait_code_otp_jour (jour, codes, utilises)
                values (date '2026-01-05', 44, 30), (date '2026-01-08', 12, 9)
                """).update();
    }

    @Test
    void usagersSansLesPaquetsAvecPartenairesEtCodesOtp() {
        RequetesUsagers u = service.usagers(null, null);

        assertThat(u.disponible()).isTrue();
        assertThat(u.perimetre()).isEqualTo("Ensemble du Togo");
        assertThat(u.requetes()).isEqualTo(58);
        // Contrôles : statuts et types forment chacun une partition des requêtes.
        assertThat(u.reussies() + u.echouees() + u.autresStatuts()).isEqualTo(u.requetes());
        assertThat(u.biometriques() + u.otp() + u.demographiquesEtCombinees() + u.sansMode() + u.nonClassees())
                .isEqualTo(u.requetes());
        assertThat(u.reussies()).isEqualTo(45);
        assertThat(u.otp()).isEqualTo(53);
        assertThat(u.partenairesRaccordes()).isEqualTo(1);
        assertThat(u.partenaires()).containsExactly("Atos");
        assertThat(u.requetesPartenaires()).isEqualTo(47);
        assertThat(u.demandesOtp()).isEqualTo(62);
        assertThat(u.demandesOtpEnvoyees()).isEqualTo(56);
        assertThat(u.codesOtp()).isEqualTo(56);
        assertThat(u.codesOtpUtilises()).isEqualTo(39);
    }

    @Test
    void laPeriodeFiltreLesJours() {
        RequetesUsagers u = service.usagers(LocalDate.parse("2026-01-01"), LocalDate.parse("2026-01-06"));

        assertThat(u.requetes()).isEqualTo(42);
        assertThat(u.codesOtp()).isEqualTo(44);
    }

    @Test
    void typesDansLOrdreDuTableauEtTotalEgalAuxRequetes() {
        TypesAuthentification t = service.types(null, null);

        assertThat(t.types()).extracting(TypesAuthentification.Type::code)
                .containsExactly("biometrique", "otp", "demographique", "combinee", "sans_mode", "non_classe");
        assertThat(t.types()).extracting(TypesAuthentification.Type::code, TypesAuthentification.Type::requetes,
                        TypesAuthentification.Type::echecs)
                .contains(tuple("otp", 53L, 8L), tuple("sans_mode", 4L, 4L), tuple("biometrique", 1L, 1L),
                        tuple("demographique", 0L, 0L));
        assertThat(t.types().stream().mapToLong(TypesAuthentification.Type::requetes).sum()).isEqualTo(58);
    }

    @Test
    void causesParPerimetreSommeEgaleAuxEchecs() {
        CausesEchec usagers = service.causes(null, null, null);
        CausesEchec paquets = service.causes("paquets", null, null);

        assertThat(usagers.echecs()).isEqualTo(13);
        assertThat(usagers.motifs()).extracting(CausesEchec.Motif::code)
                .containsExactly("OTP_REFUSE", "SANS_MODE", "AUTRE");
        assertThat(usagers.motifs().getLast().libelle()).isEqualTo("Motif non répertorié");
        assertThat(paquets.echecs()).isEqualTo(600);
        assertThat(paquets.motifs()).extracting(CausesEchec.Motif::libelle)
                .containsExactly("Biométrie non concordante");
    }

    @Test
    void partenairesEtCanauxSansCodeMosip() {
        PartenairesEtCanaux p = service.partenaires(null, null);

        assertThat(p.partenairesRaccordes()).isEqualTo(1);
        assertThat(p.appelants()).extracting(PartenairesEtCanaux.Appelant::nom, PartenairesEtCanaux.Appelant::requetes,
                        PartenairesEtCanaux.Appelant::reussies, PartenairesEtCanaux.Appelant::demandesOtp)
                .containsExactly(tuple("Atos", 47L, 35L, 50L), tuple("Portail du résident", 10L, 10L, 12L),
                        tuple("USSD", 1L, 0L, 0L));
        // Dernière requête : la plus récente des authentifications et des demandes de code.
        assertThat(p.appelants().get(1).derniereRequete()).isEqualTo(LocalDate.parse("2026-01-08"));
        assertThat(p.appelants().stream().mapToLong(PartenairesEtCanaux.Appelant::requetes).sum()).isEqualTo(58);
    }

    @Test
    void semainesDesUsagersJusquALaDerniereDonnee() {
        AuthentificationsParSemaine s = service.semaines(null, null);

        assertThat(s.semaines()).hasSize(12);
        assertThat(s.semaines().getLast().lundi()).isEqualTo(LocalDate.parse("2026-01-05"));
        assertThat(s.semaines().getLast().reussies()).isEqualTo(40);
        assertThat(s.semaines().getLast().echouees()).isEqualTo(13);
        assertThat(s.semaines().get(10).reussies()).isEqualTo(5);
    }

    @Test
    void paquetsAPartJamaisAdditionnesAuxUsagers() {
        VerificationsPaquets v = service.paquets(null, null);

        assertThat(v.disponible()).isTrue();
        assertThat(v.verifications()).isEqualTo(700);
        assertThat(v.reussies() + v.echouees() + v.autresStatuts()).isEqualTo(v.verifications());
        assertThat(service.usagers(null, null).requetes()).isEqualTo(58);
    }

    @Test
    void contraintesDuContrat() {
        // Une échouée a un motif ; une réussie n'en a pas.
        assertThatThrownBy(() -> jdbc.sql("""
                insert into bi.fait_authentification_jour values
                    (date '2026-01-09', 'usagers', 'partenaire', 'AU-ANID', 'Atos', 'otp', 'echouee', 'AUCUN', 1)
                """).update()).isInstanceOf(DataIntegrityViolationException.class);
        assertThatThrownBy(() -> jdbc.sql("""
                insert into bi.fait_code_otp_jour values (date '2026-01-09', 1, 2)
                """).update()).isInstanceOf(DataIntegrityViolationException.class);
    }

    @Test
    void sansDonneeLaSourceNEstPasDisponible() {
        jdbc.sql("truncate bi.fait_authentification_jour").update();

        assertThat(service.usagers(null, null).disponible()).isFalse();
        assertThat(service.usagers(null, null).requetes()).isNull();
        assertThat(service.paquets(null, null).disponible()).isFalse();
    }
}
