package tg.anid.bi.enrolement;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.simple.JdbcClient;

import tg.anid.bi.commun.RessourceIntrouvable;

/**
 * Suivi d'un dossier sur un PostgreSQL jetable (Testcontainers) : la ligne de bi.suivi_dossier est écrite avec
 * l'empreinte calculée par pgcrypto, comme la publication de mosip-cdc ; l'API doit la retrouver avec son propre
 * calcul (même clé). Le journal (V8) ne garde que qui, quand et le résultat.
 */
@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:tc:postgresql:17-alpine:///bi",
        "spring.datasource.driver-class-name=org.testcontainers.jdbc.ContainerDatabaseDriver",
        "spring.datasource.username=test",
        "spring.datasource.password=test",
        "spring.flyway.locations=classpath:db/migration,classpath:db/dev",
        "bi.securite.active=false",
        "bi.suivi.cle=cle-de-test"
})
class SuiviIT {

    private static final String RID = "10011100230041220261021093015";

    @Autowired
    SuiviService service;

    @Autowired
    JdbcClient jdbc;

    @BeforeEach
    void preparer() {
        jdbc.sql("create extension if not exists pgcrypto").update();
        jdbc.sql("truncate bi.suivi_dossier, bi.journal_suivi").update();
        // Empreinte calculée par PostgreSQL (pgcrypto), exactement comme scripts/publier-indicateurs.sh.
        jdbc.sql("""
                insert into bi.suivi_dossier (empreinte, centre_id, type_demande, enrole_le, synchronise_le,
                                              refus_poste, recu_le, niu_le, devenir, etape, etape_libelle,
                                              etape_statut, derniere_transaction_le, maj_le)
                select hmac(:rid, 'cle-de-test', 'sha256'), z.id, 'NEW', timestamptz '2026-10-21 09:30:15Z',
                       timestamptz '2026-10-21 10:12Z', false, timestamptz '2026-10-21 10:16Z',
                       timestamptz '2026-10-21 18:40Z', 'niu', 'UIN_GENERATOR', 'Génération du NIU', 'SUCCESS',
                       timestamptz '2026-10-21 18:41Z', now()
                from bi.zone z where z.code = '10011'
                """).param("rid", RID).update();
    }

    @Test
    void retrouveLeDossierParLEmpreinteDePgcryptoAvecSaPrefectureEtSaRegion() {
        SuiviDossier d = service.suivre(RID);

        assertThat(d.devenir()).isEqualTo("niu");
        assertThat(d.bloque()).isFalse();
        assertThat(d.centre().prefecture()).isEqualTo("Tône");
        assertThat(d.centre().region()).isEqualTo("Savanes");
        assertThat(d.etape().code()).isEqualTo("UIN_GENERATOR");
        assertThat(d.jalons().niuLe()).isNotNull();
    }

    @Test
    void chaqueRechercheEstJournaliseeSansLeRid() {
        service.suivre(RID);
        assertThatThrownBy(() -> service.suivre("10011100230041220261021093016"))
                .isInstanceOf(RessourceIntrouvable.class);

        assertThat(jdbc.sql("select resultat from bi.journal_suivi order by recherche_le, resultat")
                .query(String.class).list()).containsExactlyInAnyOrder("trouve", "introuvable");
        assertThat(jdbc.sql("select count(*) from bi.journal_suivi where utilisateur = 'anonyme'")
                .query(Long.class).single()).isEqualTo(2);
        // Aucune colonne du journal ne peut contenir le RID ni son empreinte.
        assertThat(jdbc.sql("""
                        select string_agg(column_name, ',' order by column_name)
                        from information_schema.columns
                        where table_schema = 'bi' and table_name = 'journal_suivi'
                        """).query(String.class).single()).isEqualTo("recherche_le,resultat,utilisateur");
    }
}
