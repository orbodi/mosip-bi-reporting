package tg.anid.bi.enrolement;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.simple.JdbcClient;

import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.commun.RessourceIntrouvable;

/**
 * Onglet Enrôlement de l'Exploration (lot E1) sur un PostgreSQL jetable : quatre jours d'inscriptions de trois types
 * dans trois centres (Savanes et Kara), deux jours de pré-inscriptions. Contrôle : somme des lignes = total.
 */
@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:tc:postgresql:17-alpine:///bi",
        "spring.datasource.driver-class-name=org.testcontainers.jdbc.ContainerDatabaseDriver",
        "spring.datasource.username=test",
        "spring.datasource.password=test",
        "spring.flyway.locations=classpath:db/migration,classpath:db/dev",
        "bi.securite.active=false"
})
class ExplorationEnrolementIT {

    @Autowired
    ExplorationEnrolementService service;

    @Autowired
    JdbcClient jdbc;

    @BeforeEach
    void preparer() {
        jdbc.sql("truncate bi.fait_enrolement_jour, bi.fait_preinscription_zone_jour").update();
        jdbc.sql("""
                insert into bi.fait_enrolement_jour (jour, centre_id, sexe, tranche_age, type_demande, inscriptions,
                                                     niu_generes, en_cours, echouees, rejetees)
                select cast(v.jour as date), z.id, 'I', 'inconnu', v.t, v.i, v.n, v.e, v.c, v.r
                from (values ('2025-12-20', '10011', 'NEW', 10, 8, 1, 1, 0),
                             ('2026-01-05', '10011', 'UPDATE', 5, 4, 0, 0, 1),
                             ('2026-01-06', '10012', 'NEW', 7, 6, 1, 0, 0),
                             ('2026-01-07', '10021', 'LOST', 3, 2, 0, 0, 1)) as v(jour, code, t, i, n, e, c, r)
                join bi.zone z on z.code = v.code
                """).update();
        jdbc.sql("""
                insert into bi.fait_preinscription_zone_jour (jour, zone_id, demandes)
                select cast(v.jour as date), z.id, v.d
                from (values ('2025-12-21', 'SAV-02', 4), ('2026-01-10', 'KAR-05', 6)) as v(jour, code, d)
                join bi.zone z on z.code = v.code
                """).update();
    }

    @Test
    void parRegionParMoisEtParAnneeLesLignesEgalentLeTotal() {
        ExplorationEnrolement parRegion = service.exploration(null, null, null, null, "sous");
        assertThat(parRegion.total()).isEqualTo(new ExplorationEnrolement.Chiffres(25, 20, 2, 1, 2, 10L));
        assertThat(parRegion.lignes().getFirst())
                .extracting(ExplorationEnrolement.Ligne::cle, l -> l.chiffres().inscriptions(),
                        l -> l.chiffres().preinscriptions())
                .containsExactly("SAV", 22L, 4L);
        assertThat(parRegion.lignes().stream().mapToLong(l -> l.chiffres().inscriptions()).sum()).isEqualTo(25);
        assertThat(parRegion.lignes().stream().mapToLong(l -> l.chiffres().preinscriptions()).sum()).isEqualTo(10);
        assertThat(parRegion.types()).isEmpty();

        ExplorationEnrolement parMois = service.exploration(null, null, "SAV", null, "mois");
        assertThat(parMois.perimetre()).isEqualTo("Savanes");
        assertThat(parMois.lignes()).extracting(ExplorationEnrolement.Ligne::cle).containsExactly("2025-12", "2026-01");
        assertThat(parMois.lignes().getLast().chiffres())
                .isEqualTo(new ExplorationEnrolement.Chiffres(12, 10, 1, 0, 1, 0L));

        ExplorationEnrolement parAnnee = service.exploration(null, null, null, null, "annee");
        assertThat(parAnnee.lignes()).extracting(ExplorationEnrolement.Ligne::cle).containsExactly("2025", "2026");
        assertThat(parAnnee.lignes().stream().mapToLong(l -> l.chiffres().niuGeneres()).sum()).isEqualTo(20);
    }

    @Test
    void typeDeDemandeFiltreEtVentilationSansPreinscriptions() {
        ExplorationEnrolement parType = service.exploration(null, null, null, null, "type");
        assertThat(parType.lignes()).extracting(ExplorationEnrolement.Ligne::cle)
                .containsExactly("NEW", "UPDATE", "LOST");
        assertThat(parType.total().preinscriptions()).isNull();
        assertThat(parType.lignes()).allSatisfy(l -> assertThat(l.chiffres().preinscriptions()).isNull());

        ExplorationEnrolement nouvelles = service.exploration(null, null, null, "NEW", "sous");
        assertThat(nouvelles.type()).isEqualTo("NEW");
        assertThat(nouvelles.total()).isEqualTo(new ExplorationEnrolement.Chiffres(17, 14, 2, 1, 0, null));
        assertThat(nouvelles.lignes().get(1).chiffres().inscriptions()).isZero();

        assertThat(service.exploration(null, null, null, null, "total").types())
                .containsExactly("LOST", "NEW", "UPDATE");
        assertThatThrownBy(() -> service.exploration(null, null, null, null, "sexe"))
                .isInstanceOf(RequeteInvalide.class);
        assertThatThrownBy(() -> service.exploration(null, null, "INCONNUE", null, "sous"))
                .isInstanceOf(RessourceIntrouvable.class);
    }
}
