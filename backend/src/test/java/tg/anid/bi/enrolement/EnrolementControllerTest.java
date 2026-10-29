package tg.anid.bi.enrolement;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import tg.anid.bi.commun.GestionErreurs;
import tg.anid.bi.commun.RequeteInvalide;

class EnrolementControllerTest {

    private final EnrolementService service = mock(EnrolementService.class);
    private final EnrolementTraitementService traitement = mock(EnrolementTraitementService.class);
    private MockMvc mvc;

    @BeforeEach
    void preparer() {
        mvc = MockMvcBuilders.standaloneSetup(new EnrolementController(service, traitement))
                .setControllerAdvice(new GestionErreurs())
                .build();
    }

    @Test
    void renvoieLeDevenirDesInscriptionsEnNombresBruts() throws Exception {
        LocalDate du = LocalDate.parse("2026-10-01");
        LocalDate au = LocalDate.parse("2026-10-15");
        when(service.devenir(eq(du), eq(au), isNull())).thenReturn(
                new DevenirInscriptions("Ensemble du Togo", du, au, 1000, 933, 40, 1, 26, 0, null));

        mvc.perform(get("/api/v1/enrolement/devenir").param("du", "2026-10-01").param("au", "2026-10-15"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.perimetre").value("Ensemble du Togo"))
                .andExpect(jsonPath("$.inscriptions").value(1000))
                .andExpect(jsonPath("$.niuGeneres").value(933))
                .andExpect(jsonPath("$.enCours").value(40))
                .andExpect(jsonPath("$.echouees").value(1))
                .andExpect(jsonPath("$.rejetees").value(26))
                .andExpect(jsonPath("$.nonClassees").value(0));
    }

    @Test
    void renvoieLesEtapesDArretEnCoursDelaisEtSynchronisation() throws Exception {
        when(traitement.etapes(isNull(), isNull(), isNull())).thenReturn(new ArretsParEtape("Ensemble du Togo",
                null, null, 30, 4,
                List.of(new ArretsParEtape.Etape("VALIDATE_PACKET", "Validation du paquet", 28),
                        new ArretsParEtape.Etape(null, "Autres étapes", 2)),
                List.of(new ArretsParEtape.Etape("OSI_VALIDATE", "Validation opérateur et superviseur", 4))));
        when(traitement.enCours(isNull())).thenReturn(new PaquetsEnCours("Ensemble du Togo",
                OffsetDateTime.parse("2026-10-26T08:40:00Z"), 30, 12, 5,
                List.of(new PaquetsEnCours.Etape("MANUAL_VERIFICATION", "Vérification manuelle", 12, 5))));
        when(traitement.delais(isNull(), isNull(), isNull())).thenReturn(new DelaisTraitement("Ensemble du Togo",
                null, null, new DelaisTraitement.Mesure(100, 8, 246, 70),
                new DelaisTraitement.Mesure(120, 1, 20, 115)));
        when(traitement.synchronisation(isNull())).thenReturn(new SynchronisationNonRecue("Ensemble du Togo",
                OffsetDateTime.parse("2026-10-26T08:40:00Z"), 1018, 505, OffsetDateTime.parse("2026-09-01T10:30:00Z")));

        mvc.perform(get("/api/v1/enrolement/etapes"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalRejets").value(30))
                .andExpect(jsonPath("$.rejets[1].code").doesNotExist())
                .andExpect(jsonPath("$.rejets[1].libelle").value("Autres étapes"))
                .andExpect(jsonPath("$.echecs[0].inscriptions").value(4));
        mvc.perform(get("/api/v1/enrolement/en-cours"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.seuilJours").value(30))
                .andExpect(jsonPath("$.bloques").value(5))
                .andExpect(jsonPath("$.etapes[0].code").value("MANUAL_VERIFICATION"));
        mvc.perform(get("/api/v1/enrolement/delais"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.receptionNiu.medianeH").value(8))
                .andExpect(jsonPath("$.receptionNiu.centile90H").value(246))
                .andExpect(jsonPath("$.enrolementReception.moins24h").value(115));
        mvc.perform(get("/api/v1/enrolement/synchronisation"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.nonRecus").value(1018))
                .andExpect(jsonPath("$.plusDe7Jours").value(505));
    }

    @Test
    void leClassementRemonteeEstAccepte() throws Exception {
        when(service.centres(isNull(), isNull(), isNull(), eq("remontee"))).thenReturn(new TopCentres(
                "Ensemble du Togo", "remontee",
                List.of(new TopCentres.CentreClasse(1, "10091", "EPP Mandouri", "Kpendjal", "Savanes", 412, 900))));
        mvc.perform(get("/api/v1/enrolement/centres").param("classement", "remontee"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.centres[0].valeur").value(412));
    }

    @Test
    void uneDateIllisibleEstRefusee() throws Exception {
        mvc.perform(get("/api/v1/enrolement/devenir").param("du", "15/10/2026"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void desDatesInverseesSontRefusees() throws Exception {
        when(service.devenir(any(), any(), any())).thenThrow(new RequeteInvalide("ordre des dates"));
        mvc.perform(get("/api/v1/enrolement/devenir").param("du", "2026-10-15").param("au", "2026-10-01"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void renvoieLesJoursJusquAujourdhui() throws Exception {
        when(service.jours()).thenReturn(new InscriptionsParJour("Ensemble du Togo", LocalDate.parse("2026-10-29"),
                true, List.of(new InscriptionsParJour.Jour(LocalDate.parse("2026-10-29"), 2134, 1388))));

        mvc.perform(get("/api/v1/enrolement/jours"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.aujourdhui").exists())
                .andExpect(jsonPath("$.niuDisponibles").value(true))
                .andExpect(jsonPath("$.jours[0].jour").exists())
                .andExpect(jsonPath("$.jours[0].inscriptions").value(2134))
                .andExpect(jsonPath("$.jours[0].niuGeneres").value(1388));
    }

    @Test
    void renvoieLesSemainesAvecLaDisponibiliteDesNiu() throws Exception {
        when(service.semaines(isNull(), isNull(), isNull())).thenReturn(new InscriptionsParSemaine(
                "Ensemble du Togo", null, null, false,
                List.of(new InscriptionsParSemaine.Semaine(LocalDate.parse("2026-01-05"), true, 20230, 0))));

        mvc.perform(get("/api/v1/enrolement/semaines"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.niuDisponibles").value(false))
                .andExpect(jsonPath("$.semaines.length()").value(1))
                .andExpect(jsonPath("$.semaines[0].dansLaPeriode").value(true))
                .andExpect(jsonPath("$.semaines[0].inscriptions").value(20230));
    }

    @Test
    void renvoieLeTerritoireAvecUneLigneParSousZone() throws Exception {
        when(service.territoire(isNull(), isNull(), eq("SAV"))).thenReturn(new Territoire(
                "Savanes", "SAV", "region", List.of(), null, null, 150, 130, 9, 1, 10, 0, 300, 7,
                List.of(new Territoire.LigneZone("SAV-02", "Tône", "prefecture", false, 100, 90, 4, 1, 5, 0, 180,
                                6, true),
                        new Territoire.LigneZone("SAV-01", "Cinkassé", "prefecture", false, 50, 40, 5, 0, 5, 0,
                                120, null, false))));

        mvc.perform(get("/api/v1/enrolement/territoire").param("zone", "SAV"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.perimetre").value("Savanes"))
                .andExpect(jsonPath("$.inscriptions").value(150))
                .andExpect(jsonPath("$.lignes[0].nom").value("Tône"))
                .andExpect(jsonPath("$.lignes[1].rejetees").value(5))
                .andExpect(jsonPath("$.lignes[1].horsReferentiel").value(false))
                .andExpect(jsonPath("$.delaiMedianH").value(7))
                .andExpect(jsonPath("$.lignes[0].delaiMedianH").value(6))
                .andExpect(jsonPath("$.niveau").value("region"))
                .andExpect(jsonPath("$.ascendants.length()").value(0))
                .andExpect(jsonPath("$.lignes[0].ouvrable").value(true));
    }

    @Test
    void classeLesCentresParInscriptionsParDefaut() throws Exception {
        when(service.centres(isNull(), isNull(), isNull(), eq("inscriptions"))).thenReturn(new TopCentres(
                "Ensemble du Togo", "inscriptions",
                List.of(new TopCentres.CentreClasse(1, "10011", "Centre A", "Tône", "Savanes", 43534, 43534))));

        mvc.perform(get("/api/v1/enrolement/centres"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.classement").value("inscriptions"))
                .andExpect(jsonPath("$.centres[0].rang").value(1))
                .andExpect(jsonPath("$.centres[0].region").value("Savanes"))
                .andExpect(jsonPath("$.centres[0].valeur").value(43534));
    }

    @Test
    void unClassementInconnuEstRefuse() throws Exception {
        when(service.centres(any(), any(), any(), eq("pire"))).thenThrow(new RequeteInvalide("classement"));
        mvc.perform(get("/api/v1/enrolement/centres").param("classement", "pire"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void renvoieLeProfilDesPreinscrits() throws Exception {
        when(service.profilPreinscriptions(isNull(), isNull())).thenReturn(new ProfilPreinscriptions(
                "Ensemble du Togo", null, null, true,
                List.of(new AgeSexe.Tranche("26-35", 300L, 250L)), 40L,
                List.of(new ProfilPreinscriptions.Nationalite("TOGO", 580),
                        new ProfilPreinscriptions.Nationalite("Non renseignée", 10))));

        mvc.perform(get("/api/v1/enrolement/preinscriptions/profil"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.disponible").value(true))
                .andExpect(jsonPath("$.tranches[0].femmes").value(300))
                .andExpect(jsonPath("$.nonRenseignes").value(40))
                .andExpect(jsonPath("$.nationalites[0].nom").value("TOGO"))
                .andExpect(jsonPath("$.nationalites[1].demandes").value(10));
    }

    @Test
    void renvoieLesPreinscriptionsEtNullPourLeSexe() throws Exception {
        when(service.preinscriptions(isNull(), isNull())).thenReturn(new Preinscriptions("Ensemble du Togo", null,
                null, true, 606850L, 546964L, 59886L, 0L, 0L, 450000L, 0L, null, null,
                OffsetDateTime.parse("2026-01-14T11:28:00Z")));

        mvc.perform(get("/api/v1/enrolement/preinscriptions"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.disponible").value(true))
                .andExpect(jsonPath("$.demandes").value(606850))
                .andExpect(jsonPath("$.rendezVousReserves").value(546964))
                .andExpect(jsonPath("$.enAttenteRendezVous").value(59886))
                .andExpect(jsonPath("$.honorees").value(450000))
                .andExpect(jsonPath("$.femmes").isEmpty())
                .andExpect(jsonPath("$.derniereDemande").exists());
    }

    @Test
    void renvoieLaPyramideParRegion() throws Exception {
        when(service.ageSexe(isNull(), isNull(), eq("SAV"))).thenReturn(new AgeSexe("Savanes", null, null, true,
                List.of(new AgeSexe.Tranche("0-5", 11L, 12L), new AgeSexe.Tranche("6-14", 43L, 46L)), 0L,
                List.of(new AgeSexe.Nationalite("Togo", 200), new AgeSexe.Nationalite("Non renseignée", 12))));

        mvc.perform(get("/api/v1/enrolement/age-sexe").param("zone", "SAV"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.perimetre").value("Savanes"))
                .andExpect(jsonPath("$.tranches[0].tranche").value("0-5"))
                .andExpect(jsonPath("$.tranches[1].hommes").value(46))
                .andExpect(jsonPath("$.nonRenseignes").value(0))
                .andExpect(jsonPath("$.nationalites[0].nom").value("Togo"))
                .andExpect(jsonPath("$.nationalites[1].niuGeneres").value(12));
    }
}
