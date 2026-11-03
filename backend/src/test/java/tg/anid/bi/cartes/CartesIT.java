package tg.anid.bi.cartes;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.assertj.core.api.Assertions.tuple;

import java.time.Clock;
import java.time.Instant;
import java.time.LocalDate;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.simple.JdbcClient;

import tg.anid.bi.commun.RessourceIntrouvable;
import tg.anid.bi.enrolement.EnrolementRepository;

/**
 * Page Impression des cartes sur un PostgreSQL jetable (Testcontainers) : migrations V1 à V15, référentiel de
 * développement (centres 10011 Tône et 10012 Cinkassé en Savanes, 10021 Kozah en Kara), faits écrits directement comme
 * les publie le pipeline. Dernière donnée d'impression du référentiel de développement : mercredi 14/01/2026, donc
 * dernière semaine complète du 05/01 au 11/01/2026.
 */
@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:tc:postgresql:17-alpine:///bi",
        "spring.datasource.driver-class-name=org.testcontainers.jdbc.ContainerDatabaseDriver",
        "spring.datasource.username=test",
        "spring.datasource.password=test",
        "spring.flyway.locations=classpath:db/migration,classpath:db/dev",
        "bi.securite.active=false"
})
class CartesIT {

    @Autowired
    CartesService service;

    @Autowired
    CartesRepository repository;

    @Autowired
    EnrolementRepository zones;

    @Autowired
    JdbcClient jdbc;

    @BeforeEach
    void preparer() {
        jdbc.sql("""
                truncate bi.fait_demande_impression_jour, bi.fait_carte_jour, bi.fait_delai_carte_jour,
                         bi.fait_annulation_impression_jour
                """).update();
        jdbc.sql("""
                insert into bi.fait_demande_impression_jour (jour, centre_id, demandes, envoyees, en_attente, rejetees,
                                                             non_classees, annulees)
                select v.jour, z.id, v.dem, v.env, v.att, v.rej, 0, v.ann
                from (values (date '2026-01-05', '10011', 100, 95, 4, 1, 2),
                             (date '2026-01-06', '10012',  50, 50, 0, 0, 0),
                             (date '2026-01-07', '10021',  80, 78, 0, 2, 1),
                             (date '2025-12-29', 'CENTRE_NON_REFERENCE', 10, 10, 0, 0, 0))
                     as v (jour, code, dem, env, att, rej, ann)
                join bi.zone z on z.code = v.code
                """).update();
        // Cartes : une expédiée en juin 2025 (plus de 180 jours au 14/01/2026), les autres en janvier 2026.
        jdbc.sql("""
                insert into bi.fait_carte_jour (jour, centre_id, expediees, remises, remises_hors_ligne,
                                                remises_en_ligne, remises_support, remises_autre, a_remettre)
                select v.jour, z.id, v.exp, v.rem, v.rem - v.lig, v.lig, 0, 0, v.exp - v.rem
                from (values (date '2026-01-08', '10011', 90, 60, 10),
                             (date '2026-01-09', '10012', 40, 40, 0),
                             (date '2026-01-09', '10021', 70, 20, 5),
                             (date '2025-06-02', '10021', 10, 0, 0))
                     as v (jour, code, exp, rem, lig)
                join bi.zone z on z.code = v.code
                """).update();
        jdbc.sql("""
                insert into bi.fait_delai_carte_jour (jour, centre_id, classe_j, cartes)
                select v.jour, z.id, v.classe, v.cartes
                from (values (date '2026-01-08', '10011', 20, 30), (date '2026-01-08', '10011', 40, 30),
                             (date '2026-01-09', '10012', 30, 40), (date '2026-01-09', '10021', 120, 20))
                     as v (jour, code, classe, cartes)
                join bi.zone z on z.code = v.code
                """).update();
        jdbc.sql("""
                insert into bi.fait_annulation_impression_jour (jour, centre_id, motif, motif_libelle, demandes)
                select v.jour, z.id, v.motif, v.libelle, v.n
                from (values (date '2026-01-05', '10011', 'CANCEL_PHOTO', 'Photo à reprendre', 2),
                             (date '2026-01-07', '10021', 'CANCEL_SEX', 'Sexe à corriger', 1))
                     as v (jour, code, motif, libelle, n)
                join bi.zone z on z.code = v.code
                """).update();
    }

    @Test
    void impressionNationaleEtSesEgalitesDeControle() {
        ImpressionRemise i = service.impression(null, null, null);

        assertThat(i.disponible()).isTrue();
        assertThat(i.demandes()).isEqualTo(240);
        assertThat(i.envoyees() + i.enAttente() + i.rejetees() + i.nonClassees()).isEqualTo(i.demandes());
        assertThat(i.enAttente()).isEqualTo(4);
        assertThat(i.rejetees()).isEqualTo(3);
        assertThat(i.derniereRejetee()).isEqualTo("2026-01-07");
        assertThat(i.annulees()).isEqualTo(3);
        assertThat(i.expediees()).isEqualTo(210);
        assertThat(i.remises()).isEqualTo(120);
        assertThat(i.remises() + i.aRemettre()).isEqualTo(i.expediees());
        assertThat(i.remisesHorsLigne() + i.remisesEnLigne() + i.remisesSupport() + i.remisesAutre())
                .isEqualTo(i.remises());
        assertThat(i.remisesEnLigne()).isEqualTo(15);
        // Histogramme : 30 à 20 j, 40 à 30 j, 30 à 40 j, 20 à 120 j ; la 60e carte sur 120 tombe dans la classe 30.
        assertThat(i.delaiMedianJours()).isEqualTo(30);
    }

    @Test
    void impressionDUneRegionEtDUnePeriode() {
        ImpressionRemise savanes = service.impression(null, null, "SAV");
        assertThat(savanes.perimetre()).isEqualTo("Savanes");
        assertThat(savanes.demandes()).isEqualTo(150);
        assertThat(savanes.expediees()).isEqualTo(130);
        assertThat(savanes.delaiMedianJours()).isEqualTo(30);

        ImpressionRemise janvier = service.impression(LocalDate.parse("2026-01-01"), LocalDate.parse("2026-01-31"), null);
        assertThat(janvier.demandes()).isEqualTo(230);
        assertThat(janvier.expediees()).isEqualTo(200);
    }

    @Test
    void sansDonneesLeBlocEstNonDisponible() {
        jdbc.sql("truncate bi.fait_demande_impression_jour").update();

        ImpressionRemise i = service.impression(null, null, null);
        assertThat(i.disponible()).isFalse();
        assertThat(i.demandes()).isNull();
        assertThat(i.delaiMedianJours()).isNull();
    }

    @Test
    void douzeSemainesJusquALaDerniereDonneeDImpression() {
        ImpressionsParSemaine s = service.semaines(null, null, null);

        assertThat(s.semaines()).hasSize(12);
        assertThat(s.semaines().getLast().lundi()).isEqualTo("2026-01-05");
        assertThat(s.semaines().getLast().demandes()).isEqualTo(230);
        assertThat(s.semaines().getLast().expediees()).isEqualTo(200);
        assertThat(s.semaines().getLast().rejetees()).isEqualTo(3);
        assertThat(s.semaines().get(10).demandes()).isEqualTo(10);
    }

    @Test
    void territoireNationalLignesEgalesAuxTotaux() {
        TerritoireCartes t = service.territoire(null, null, null);
        ImpressionRemise i = service.impression(null, null, null);

        assertThat(t.expediees()).isEqualTo(i.expediees());
        assertThat(t.remises() + t.aRemettre()).isEqualTo(t.expediees());
        assertThat(t.lignes()).extracting(TerritoireCartes.LigneZone::code)
                .containsExactly("SAV", "KAR", "CEN", "PLA", "MAR", "GLO");
        assertThat(t.lignes().stream().mapToLong(TerritoireCartes.LigneZone::expediees).sum())
                .isEqualTo(t.expediees());
        assertThat(t.lignes().stream().mapToLong(TerritoireCartes.LigneZone::aRemettre).sum())
                .isEqualTo(t.aRemettre());
        assertThat(t.lignes()).allSatisfy(l -> assertThat(l.remises() + l.aRemettre()).isEqualTo(l.expediees()));
    }

    @Test
    void territoireDUneRegionEtZoneInconnue() {
        TerritoireCartes kara = service.territoire(null, null, "KAR");
        assertThat(kara.niveau()).isEqualTo("region");
        assertThat(kara.expediees()).isEqualTo(80);
        assertThat(kara.lignes()).allSatisfy(l -> assertThat(l.niveau()).isEqualTo("prefecture"));

        assertThatThrownBy(() -> service.territoire(null, null, "INCONNUE"))
                .isInstanceOf(RessourceIntrouvable.class);
    }

    @Test
    void attenteParAncienneteDepuisLExpedition() {
        // Ancienneté calculée au mercredi 14/01/2026 (horloge fixe) : 30 + 50 cartes de janvier, 10 de juin 2025.
        CartesService auQuatorzeJanvier = new CartesService(repository, zones,
                Clock.fixed(Instant.parse("2026-01-14T10:00:00Z"), CartesService.TOGO));
        CartesEnAttente a = auQuatorzeJanvier.attente(null, null, null);
        ImpressionRemise i = service.impression(null, null, null);

        assertThat(a.calculeLe()).isEqualTo("2026-01-14");
        assertThat(a.aRemettre()).isEqualTo(i.aRemettre()).isEqualTo(90);
        assertThat(a.tranches()).extracting(CartesEnAttente.Tranche::code, CartesEnAttente.Tranche::cartes)
                .containsExactly(tuple("moins_30j", 80L), tuple("30_90j", 0L), tuple("90_180j", 0L),
                        tuple("plus_180j", 10L));
    }

    @Test
    void topDesCentresParCartesRemises() {
        TopCentresCartes t = service.centres(null, null, null);

        assertThat(t.centres()).extracting(TopCentresCartes.CentreClasse::code)
                .containsExactly("10011", "10012", "10021");
        assertThat(t.centres().getFirst().remises()).isEqualTo(60);
        assertThat(t.centres().getFirst().expediees()).isEqualTo(90);
        assertThat(t.centres().getFirst().region()).isEqualTo("Savanes");
    }

    @Test
    void lesContraintesDeV15RefusentDesChiffresIncoherents() {
        assertThatThrownBy(() -> jdbc.sql("update bi.fait_carte_jour set a_remettre = a_remettre + 1").update())
                .hasMessageContaining("fait_carte_jour_remises");
        assertThatThrownBy(() -> jdbc.sql("update bi.fait_demande_impression_jour set annulees = demandes + 1")
                .update()).hasMessageContaining("fait_demande_impression_jour_annulees");
    }

    @Test
    void annulationsParMotifEgalesAuxAnnulees() {
        AnnulationsParMotif a = service.annulations(null, null, null);

        assertThat(a.total()).isEqualTo(service.impression(null, null, null).annulees());
        assertThat(a.motifs()).extracting(AnnulationsParMotif.Motif::code)
                .containsExactly("CANCEL_PHOTO", "CANCEL_SEX");
    }
}
