package tg.anid.bi.enrolement;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.LocalDate;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.simple.JdbcClient;

/**
 * Blocs du traitement (migration V7) sur un PostgreSQL jetable (Testcontainers), référentiel de développement :
 * centres 10011 (Tône, Savanes), 10012 (Cinkassé, Savanes), 10021 (Kozah, Kara). Les égalités de contrôle avec le
 * bloc « Devenir » sont vérifiées sur les mêmes faits.
 */
@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:tc:postgresql:17-alpine:///bi",
        "spring.datasource.driver-class-name=org.testcontainers.jdbc.ContainerDatabaseDriver",
        "spring.datasource.username=test",
        "spring.datasource.password=test",
        "spring.flyway.locations=classpath:db/migration,classpath:db/dev",
        "bi.securite.active=false"
})
class TraitementIT {

    @Autowired
    EnrolementTraitementService traitement;

    @Autowired
    EnrolementService service;

    @Autowired
    JdbcClient jdbc;

    @BeforeEach
    void preparer() {
        jdbc.sql("""
                truncate bi.fait_enrolement_jour, bi.fait_arret_etape_jour, bi.stock_en_cours,
                         bi.stock_synchro_non_recue, bi.fait_delai_jour, bi.fait_arret_motif_jour,
                         bi.stock_en_cours_motif
                """).update();
        // Faits : 10011 : 100 paquets (80 NIU, 6 en cours, 4 échoués, 10 rejetés) ; 10021 : 50 (45 NIU, 3 en cours,
        // 0 échoué, 2 rejetés).
        jdbc.sql("""
                insert into bi.fait_enrolement_jour (jour, centre_id, sexe, tranche_age, type_demande, inscriptions,
                                                     niu_generes, en_cours, echouees, rejetees, non_classees)
                select v.jour, z.id, 'I', 'inconnu', 'NEW', v.ins, v.niu, v.cours, v.ech, v.rej, 0
                from (values (date '2026-01-05', '10011', 100, 80, 6, 4, 10),
                             (date '2026-01-07', '10021', 50, 45, 3, 0, 2))
                     as v (jour, code, ins, niu, cours, ech, rej)
                join bi.zone z on z.code = v.code
                """).update();
        jdbc.sql("""
                insert into bi.fait_arret_etape_jour (jour, centre_id, type_demande, devenir, etape, etape_libelle,
                                                      etape_ordre, inscriptions)
                select v.jour, z.id, 'NEW', v.devenir, v.etape, v.libelle, v.ordre, v.n
                from (values (date '2026-01-05', '10011', 'rejete', 'REFUS_POSTE', 'Refus au poste', 25, 7),
                             (date '2026-01-05', '10011', 'rejete', 'DEMOGRAPHIC_VERIFICATION',
                              'Déduplication démographique', 50, 3),
                             (date '2026-01-05', '10011', 'echoue', 'OSI_VALIDATE',
                              'Validation opérateur et superviseur', 45, 4),
                             (date '2026-01-07', '10021', 'rejete', 'REFUS_POSTE', 'Refus au poste', 25, 2))
                     as v (jour, code, devenir, etape, libelle, ordre, n)
                join bi.zone z on z.code = v.code
                """).update();
        jdbc.sql("""
                insert into bi.stock_en_cours (centre_id, type_demande, etape, etape_libelle, etape_ordre, anciennete,
                                               inscriptions, calcule_le)
                select z.id, 'NEW', v.etape, v.libelle, v.ordre, v.anciennete, v.n, timestamptz '2026-01-14 11:50Z'
                from (values ('10011', 'MANUAL_VERIFICATION', 'Vérification manuelle', 55, 'plus_30j', 4),
                             ('10011', 'MANUAL_VERIFICATION', 'Vérification manuelle', 55, 'moins_7j', 1),
                             ('10011', 'PACKET_RECEIVER', 'Réception du paquet', 10, 'moins_7j', 1),
                             ('10021', 'PACKET_RECEIVER', 'Réception du paquet', 10, '7_30j', 3))
                     as v (code, etape, libelle, ordre, anciennete, n)
                join bi.zone z on z.code = v.code
                """).update();
        // Motifs (V9), mêmes totaux : rejetés 10 (Tône, 05/01) + 2 (Kozah, 07/01), échoués 4, en cours 6 + 3.
        jdbc.sql("""
                insert into bi.fait_arret_motif_jour (jour, centre_id, type_demande, devenir, stage, stage_libelle,
                                                      stage_ordre, motif, motif_libelle, motif_commentaire,
                                                      motif_piste, inscriptions)
                select v.jour, z.id, 'NEW', v.devenir, v.stage, v.stage_libelle, v.ordre, v.motif, v.libelle,
                       v.commentaire, case when v.motif = 'REFUS_SUPERVISEUR' then 'La personne doit se réenrôler.' end,
                       v.n
                from (values (date '2026-01-05', '10011', 'rejete', 'PacketValidatorStage', 'Validation du paquet', 30,
                              'REFUS_SUPERVISEUR', 'Refusé par le superviseur du centre', 'Rejected by Supervisor', 7),
                             (date '2026-01-05', '10011', 'rejete', 'DemoDedupeStage', 'Déduplication démographique',
                              50, 'DOUBLON_ABIS', 'Doublon : empreintes, iris ou visage déjà enregistrés',
                              'Biometric Duplicate was Found in ABIS', 3),
                             (date '2026-01-05', '10011', 'echoue', 'OSIValidatorStage', 'Validation de l''agent', 45,
                              'BIOMETRIE_NON_CONCORDANTE', 'Vérification biométrique non concordante',
                              'Biometric data did not match', 4),
                             (date '2026-01-07', '10021', 'rejete', 'PacketValidatorStage', 'Validation du paquet', 30,
                              'REFUS_SUPERVISEUR', 'Refusé par le superviseur du centre', 'Rejected by Supervisor', 2))
                     as v (jour, code, devenir, stage, stage_libelle, ordre, motif, libelle, commentaire, n)
                join bi.zone z on z.code = v.code
                """).update();
        jdbc.sql("""
                insert into bi.stock_en_cours_motif (centre_id, type_demande, stage, stage_libelle, stage_ordre, motif,
                                                     motif_libelle, motif_commentaire, anciennete, inscriptions,
                                                     calcule_le)
                select z.id, 'NEW', v.stage, v.stage_libelle, v.ordre, v.motif, v.libelle, v.commentaire, v.anciennete,
                       v.n, timestamptz '2026-01-14 11:50Z'
                from (values ('10011', 'BioDedupeStage', 'Déduplication biométrique', 55, 'FILE_VERIF_MANUELLE',
                              'En attente de vérification manuelle', 'Manual verification Sent to queue', 'plus_30j', 4),
                             ('10011', 'BioDedupeStage', 'Déduplication biométrique', 55, 'FILE_VERIF_MANUELLE',
                              'En attente de vérification manuelle', 'Manual verification Sent to queue', 'moins_7j', 1),
                             ('10011', 'PacketReceiverStage', 'Réception du paquet', 10, 'RECU_EN_ATTENTE',
                              'Reçu, en attente de traitement', 'Packet is Uploaded to Landing Zone', 'moins_7j', 1),
                             ('10021', 'PacketReceiverStage', 'Réception du paquet', 10, 'RECU_EN_ATTENTE',
                              'Reçu, en attente de traitement', 'Packet is Uploaded to Landing Zone', '7_30j', 3))
                     as v (code, stage, stage_libelle, ordre, motif, libelle, commentaire, anciennete, n)
                join bi.zone z on z.code = v.code
                """).update();
        jdbc.sql("""
                insert into bi.stock_synchro_non_recue (centre_id, anciennete, paquets, plus_ancienne_le, calcule_le)
                select z.id, v.anciennete, v.n, v.depuis, timestamptz '2026-01-14 11:50Z'
                from (values ('10011', 'moins_7j', 5, timestamptz '2026-01-12 08:00Z'),
                             ('10012', 'plus_7j', 2, timestamptz '2025-12-20 09:00Z'),
                             ('10021', 'plus_7j', 6, timestamptz '2025-12-01 10:00Z'))
                     as v (code, anciennete, n, depuis)
                join bi.zone z on z.code = v.code
                """).update();
        // Délais : réception → NIU (NEW) : 3 à 2 h, 2 à 10 h, 4 à 30 h, 1 à 72 h ; un renouvellement (UPDATE) ignoré.
        // Enrôlement → réception : 6 à 0 h, 3 à 20 h, 1 à 50 h.
        jdbc.sql("""
                insert into bi.fait_delai_jour (jour, centre_id, type_demande, mesure, classe_h, paquets)
                select v.jour, z.id, v.type, v.mesure, v.classe, v.n
                from (values (date '2026-01-08', '10011', 'NEW', 'reception_niu', 2, 3),
                             (date '2026-01-08', '10011', 'NEW', 'reception_niu', 10, 2),
                             (date '2026-01-09', '10021', 'NEW', 'reception_niu', 30, 4),
                             (date '2026-01-10', '10021', 'NEW', 'reception_niu', 72, 1),
                             (date '2026-01-10', '10021', 'UPDATE', 'reception_niu', 400, 9),
                             (date '2026-01-05', '10011', 'NEW', 'enrolement_reception', 0, 6),
                             (date '2026-01-05', '10011', 'UPDATE', 'enrolement_reception', 20, 3),
                             (date '2026-01-07', '10021', 'NEW', 'enrolement_reception', 50, 1))
                     as v (jour, code, type, mesure, classe, n)
                join bi.zone z on z.code = v.code
                """).update();
    }

    @Test
    void etapesDArretEgalesAuDevenirSurLaMemeZoneEtLaMemePeriode() {
        ArretsParEtape togo = traitement.etapes(null, null, null);
        DevenirInscriptions d = service.devenir(null, null, null);

        assertThat(togo.rejets()).extracting(ArretsParEtape.Etape::code)
                .containsExactly("REFUS_POSTE", "DEMOGRAPHIC_VERIFICATION");
        assertThat(togo.rejets().getFirst().inscriptions()).isEqualTo(9);
        assertThat(togo.totalRejets()).isEqualTo(d.rejetees()).isEqualTo(12);
        assertThat(togo.totalEchecs()).isEqualTo(d.echouees()).isEqualTo(4);

        ArretsParEtape kara = traitement.etapes(null, null, "KAR");
        assertThat(kara.perimetre()).isEqualTo("Kara");
        assertThat(kara.totalRejets()).isEqualTo(service.devenir(null, null, "KAR").rejetees()).isEqualTo(2);
        assertThat(kara.echecs()).isEmpty();

        // Période : seul le 05/01 (Tône).
        LocalDate jour = LocalDate.parse("2026-01-05");
        assertThat(traitement.etapes(jour, jour, null).totalRejets())
                .isEqualTo(service.devenir(jour, jour, null).rejetees()).isEqualTo(10);
    }

    @Test
    void enCoursEgalAuDevenirSansPeriodeEtBloquesDansLeDevenir() {
        PaquetsEnCours p = traitement.enCours(null);
        DevenirInscriptions d = service.devenir(null, null, null);

        assertThat(p.total()).isEqualTo(d.enCours()).isEqualTo(9);
        assertThat(p.bloques()).isEqualTo(4);
        assertThat(d.bloques()).isEqualTo(4);
        assertThat(p.etapes()).extracting(PaquetsEnCours.Etape::code)
                .containsExactly("PACKET_RECEIVER", "MANUAL_VERIFICATION");
        assertThat(p.calculeLe()).isNotNull();
        // Avec une période, le stock n'est pas daté : pas de « dont bloqués ».
        assertThat(service.devenir(LocalDate.parse("2026-01-01"), null, null).bloques()).isNull();
        assertThat(traitement.enCours("KAR").total()).isEqualTo(service.devenir(null, null, "KAR").enCours());
    }

    @Test
    void motifsEgauxAuDevenirTriesParNombre() {
        MotifsArret togo = traitement.motifs(null, null, null);
        DevenirInscriptions d = service.devenir(null, null, null);

        // Rejetés : Refus par le superviseur (7 + 2 = 9) puis doublon ABIS (3), du plus fréquent au moins fréquent.
        assertThat(togo.rejets()).extracting(MotifsArret.Ligne::motif, MotifsArret.Ligne::inscriptions)
                .containsExactly(org.assertj.core.groups.Tuple.tuple("REFUS_SUPERVISEUR", 9L),
                        org.assertj.core.groups.Tuple.tuple("DOUBLON_ABIS", 3L));
        assertThat(togo.rejets().getFirst().commentaire()).isEqualTo("Rejected by Supervisor");
        assertThat(togo.rejets().getFirst().piste()).isEqualTo("La personne doit se réenrôler.");
        assertThat(togo.enCours().getFirst().piste()).isNull();
        assertThat(togo.rejets().getFirst().stageLibelle()).isEqualTo("Validation du paquet");
        assertThat(togo.totalRejets()).isEqualTo(d.rejetees()).isEqualTo(12);
        assertThat(togo.totalEchecs()).isEqualTo(d.echouees()).isEqualTo(4);
        assertThat(togo.totalEnCours()).isEqualTo(d.enCours()).isEqualTo(9);
        assertThat(togo.bloques()).isEqualTo(d.bloques()).isEqualTo(4);
        assertThat(togo.enCours().getFirst()).extracting(MotifsArret.Ligne::motif, MotifsArret.Ligne::inscriptions,
                        MotifsArret.Ligne::bloques)
                .containsExactly("FILE_VERIF_MANUELLE", 5L, 4L);
        assertThat(togo.calculeLe()).isNotNull();

        MotifsArret kara = traitement.motifs(null, null, "KAR");
        assertThat(kara.perimetre()).isEqualTo("Kara");
        assertThat(kara.totalRejets()).isEqualTo(service.devenir(null, null, "KAR").rejetees()).isEqualTo(2);
        assertThat(kara.totalEnCours()).isEqualTo(3);
        assertThat(kara.echecs()).isEmpty();

        LocalDate jour = LocalDate.parse("2026-01-05");
        assertThat(traitement.motifs(jour, jour, null).totalRejets())
                .isEqualTo(service.devenir(jour, jour, null).rejetees()).isEqualTo(10);
    }

    @Test
    void delaisMedianEtCentileEnHeures() {
        DelaisTraitement t = traitement.delais(null, null, null);

        assertThat(t.receptionNiu().paquets()).isEqualTo(10);
        assertThat(t.receptionNiu().medianeH()).isEqualTo(10);
        assertThat(t.receptionNiu().centile90H()).isEqualTo(30);
        assertThat(t.enrolementReception().paquets()).isEqualTo(10);
        assertThat(t.enrolementReception().moins24h()).isEqualTo(9);
        assertThat(t.enrolementReception().medianeH()).isZero();

        DelaisTraitement savanes = traitement.delais(null, null, "SAV");
        assertThat(savanes.receptionNiu().paquets()).isEqualTo(5);
        assertThat(savanes.receptionNiu().medianeH()).isEqualTo(2);
    }

    @Test
    void synchronisesNonRecusEtRemonteeLaPlusLente() {
        SynchronisationNonRecue togo = traitement.synchronisation(null);
        assertThat(togo.nonRecus()).isEqualTo(13);
        assertThat(togo.plusDe7Jours()).isEqualTo(8);
        assertThat(togo.plusAncienneLe()).isNotNull();
        assertThat(traitement.synchronisation("SAV").plusDe7Jours()).isEqualTo(2);

        // Remontée la plus lente : paquets non reçus depuis plus de 7 jours, même sans réception sur la période
        // (Cinkassé, 10012, n'a aucune inscription).
        TopCentres top = service.centres(null, null, null, "remontee");
        assertThat(top.centres()).extracting(TopCentres.CentreClasse::code, TopCentres.CentreClasse::valeur)
                .containsExactly(org.assertj.core.groups.Tuple.tuple("10021", 6L),
                        org.assertj.core.groups.Tuple.tuple("10012", 2L));
    }
}
