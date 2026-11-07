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
 * Onglet Enrôlement de l'Exploration (lots E1 et E2) sur un PostgreSQL jetable : quatre jours d'inscriptions de trois
 * types dans trois centres (Savanes et Kara), dont une partie avec profil (sexe, tranche d'âge, nationalité de l'ID
 * Repository), deux jours de pré-inscriptions. Contrôle : somme des lignes = total.
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
        // Mêmes totaux que le lot E1 (25 inscriptions, 20 NIU) ; profil connu pour 14 NIU, « I » ailleurs.
        jdbc.sql("""
                insert into bi.fait_enrolement_jour (jour, centre_id, sexe, tranche_age, type_demande, nationalite,
                                                     inscriptions, niu_generes, en_cours, echouees, rejetees)
                select cast(v.jour as date), z.id, v.s, v.a, v.t, v.n, v.i, v.g, v.e, v.c, v.r
                from (values ('2025-12-20', '10011', 'F', '26-35', 'NEW', 'TOGO', 6, 6, 0, 0, 0),
                             ('2025-12-20', '10011', 'I', 'inconnu', 'NEW', 'Non renseignée', 4, 2, 1, 1, 0),
                             ('2026-01-05', '10011', 'H', '0-5', 'UPDATE', 'BENIN', 4, 4, 0, 0, 0),
                             ('2026-01-05', '10011', 'I', 'inconnu', 'UPDATE', 'Non renseignée', 1, 0, 0, 0, 1),
                             ('2026-01-06', '10012', 'F', '60+', 'NEW', 'TOGO', 4, 4, 0, 0, 0),
                             ('2026-01-06', '10012', 'I', 'inconnu', 'NEW', 'Non renseignée', 3, 2, 1, 0, 0),
                             ('2026-01-07', '10021', 'I', 'inconnu', 'LOST', 'Non renseignée', 3, 2, 0, 0, 1))
                     as v(jour, code, s, a, t, n, i, g, e, c, r)
                join bi.zone z on z.code = v.code
                """).update();
        jdbc.sql("""
                insert into bi.fait_preinscription_zone_jour (jour, zone_id, demandes)
                select cast(v.jour as date), z.id, v.d
                from (values ('2025-12-21', 'SAV-02', 4), ('2026-01-10', 'KAR-05', 6)) as v(jour, code, d)
                join bi.zone z on z.code = v.code
                """).update();
    }

    private static ExplorationEnrolementRepository.Filtres type(String type) {
        return new ExplorationEnrolementRepository.Filtres(type, null, null, null);
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

        ExplorationEnrolement nouvelles = service.exploration(null, null, null, type("NEW"), "sous");
        assertThat(nouvelles.type()).isEqualTo("NEW");
        assertThat(nouvelles.total()).isEqualTo(new ExplorationEnrolement.Chiffres(17, 14, 2, 1, 0, null));
        assertThat(nouvelles.lignes().get(1).chiffres().inscriptions()).isZero();

        ExplorationEnrolement valeurs = service.exploration(null, null, null, null, "total");
        assertThat(valeurs.types()).containsExactly("LOST", "NEW", "UPDATE");
        assertThat(valeurs.nationalites()).containsExactly("Non renseignée", "TOGO", "BENIN");
        assertThatThrownBy(() -> service.exploration(null, null, "INCONNUE", null, "sous"))
                .isInstanceOf(RessourceIntrouvable.class);
    }

    @Test
    void sexeTrancheEtNationaliteSeulementPourLesInscriptionsAvecProfil() {
        ExplorationEnrolement parSexe = service.exploration(null, null, null, null, "sexe");
        assertThat(parSexe.lignes()).extracting(ExplorationEnrolement.Ligne::cle).containsExactly("F", "H", "I");
        assertThat(parSexe.lignes().getFirst().chiffres()).isEqualTo(
                new ExplorationEnrolement.Chiffres(10, 10, 0, 0, 0, null));
        assertThat(parSexe.lignes().stream().mapToLong(l -> l.chiffres().inscriptions()).sum()).isEqualTo(25);

        ExplorationEnrolement parAge = service.exploration(null, null, "SAV", null, "age");
        assertThat(parAge.lignes()).extracting(ExplorationEnrolement.Ligne::cle)
                .containsExactly("0-5", "26-35", "60+", "inconnu");

        ExplorationEnrolement parNationalite = service.exploration(null, null, null, null, "nationalite");
        assertThat(parNationalite.lignes()).extracting(ExplorationEnrolement.Ligne::cle)
                .containsExactly("Non renseignée", "TOGO", "BENIN");

        // Femmes togolaises de 26 à 35 ans en nouvelle inscription : 6, sans pré-inscriptions.
        ExplorationEnrolement filtre = service.exploration(null, null, null,
                new ExplorationEnrolementRepository.Filtres("NEW", "F", "26-35", "TOGO"), "sous");
        assertThat(filtre.total()).isEqualTo(new ExplorationEnrolement.Chiffres(6, 6, 0, 0, 0, null));
        assertThat(filtre.lignes().getFirst().chiffres().inscriptions()).isEqualTo(6);
        assertThatThrownBy(() -> service.exploration(null, null, null, null, "region"))
                .isInstanceOf(RequeteInvalide.class);
    }
}
