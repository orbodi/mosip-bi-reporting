package tg.anid.bi.authentifications;

import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.time.LocalDate;
import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import tg.anid.bi.commun.GestionErreurs;
import tg.anid.bi.commun.RequeteInvalide;

class AuthentificationsControllerTest {

    private final AuthentificationsService service = mock(AuthentificationsService.class);
    private MockMvc mvc;

    @BeforeEach
    void preparer() {
        mvc = MockMvcBuilders.standaloneSetup(new AuthentificationsController(service))
                .setControllerAdvice(new GestionErreurs())
                .build();
    }

    @Test
    void renvoieLesUsagersEnNombresBruts() throws Exception {
        LocalDate du = LocalDate.parse("2026-10-01");
        when(service.usagers(eq(du), isNull())).thenReturn(new RequetesUsagers("Ensemble du Togo", du, null, true,
                2186L, 1538L, 648L, 0L, 1L, 1955L, 0L, 230L, 0L, 1L, 1645L, List.of("Atos"), 2732L, 2380L, 83873L,
                50781L));

        mvc.perform(get("/api/v1/authentifications/usagers").param("du", "2026-10-01"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.disponible").value(true))
                .andExpect(jsonPath("$.requetes").value(2186))
                .andExpect(jsonPath("$.echouees").value(648))
                .andExpect(jsonPath("$.otp").value(1955))
                .andExpect(jsonPath("$.partenaires[0]").value("Atos"))
                .andExpect(jsonPath("$.codesOtpUtilises").value(50781));
    }

    @Test
    void renvoieLesPartenairesSansCodeEtLesCausesDesPaquets() throws Exception {
        when(service.partenaires(isNull(), isNull())).thenReturn(new PartenairesEtCanaux(null, null, 1, List.of(
                new PartenairesEtCanaux.Appelant("partenaire", "Atos", 1645, 1142, 2159,
                        LocalDate.parse("2026-11-03")))));
        when(service.causes(eq("paquets"), isNull(), isNull())).thenReturn(new CausesEchec("paquets", null, null,
                106076, List.of(new CausesEchec.Motif("BIO_NON_CONCORDANTE", "Biométrie non concordante", 106076))));

        mvc.perform(get("/api/v1/authentifications/partenaires"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.appelants[0].nom").value("Atos"))
                .andExpect(jsonPath("$.appelants[0].derniereRequete").value("2026-11-03"))
                .andExpect(jsonPath("$.appelants[0].appelantId").doesNotExist());
        mvc.perform(get("/api/v1/authentifications/causes").param("perimetre", "paquets"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.motifs[0].code").value("BIO_NON_CONCORDANTE"));
    }

    @Test
    void uneRequeteInvalideRepond400() throws Exception {
        when(service.usagers(eq(LocalDate.parse("2026-10-31")), eq(LocalDate.parse("2026-10-01"))))
                .thenThrow(new RequeteInvalide("La date « du » doit précéder la date « au »."));

        mvc.perform(get("/api/v1/authentifications/usagers").param("du", "2026-10-31").param("au", "2026-10-01"))
                .andExpect(status().isBadRequest());
        mvc.perform(get("/api/v1/authentifications/types").param("du", "31/10/26"))
                .andExpect(status().isBadRequest());
    }
}
