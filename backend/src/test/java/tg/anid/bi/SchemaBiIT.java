package tg.anid.bi;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import tg.anid.bi.meta.FraicheurSource;
import tg.anid.bi.meta.Meta;
import tg.anid.bi.meta.MetaController;

/**
 * Démarre l'application sur un PostgreSQL jetable (Testcontainers, Docker requis), applique les migrations Flyway
 * et les données de démonstration, puis lit la fraîcheur des sources. Lancé par « mvn verify ».
 */
@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:tc:postgresql:17-alpine:///bi",
        "spring.datasource.driver-class-name=org.testcontainers.jdbc.ContainerDatabaseDriver",
        "spring.datasource.username=test",
        "spring.datasource.password=test",
        "spring.flyway.locations=classpath:db/migration,classpath:db/dev",
        "bi.securite.active=false"
})
class SchemaBiIT {

    @Autowired
    MetaController controller;

    @Test
    void lesMigrationsEtLesDonneesDeDemonstrationSontAppliquees() {
        Meta meta = controller.meta();

        assertThat(meta.sources())
                .extracting(FraicheurSource::source)
                .containsExactly("enrolement", "cartes", "abis", "idps", "authentifications", "preinscription");
        assertThat(meta.sources().get(0).premiereDonnee()).hasToString("2024-01-01");
        assertThat(meta.sources().get(0).derniereDonnee()).isNotNull();
    }
}
