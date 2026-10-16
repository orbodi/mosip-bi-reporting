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

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import tg.anid.bi.commun.GestionErreurs;
import tg.anid.bi.commun.RequeteInvalide;

class EnrolementControllerTest {

    private final EnrolementService service = mock(EnrolementService.class);
    private MockMvc mvc;

    @BeforeEach
    void preparer() {
        mvc = MockMvcBuilders.standaloneSetup(new EnrolementController(service))
                .setControllerAdvice(new GestionErreurs())
                .build();
    }

    @Test
    void renvoieLeDevenirDesInscriptionsEnNombresBruts() throws Exception {
        LocalDate du = LocalDate.parse("2026-10-01");
        LocalDate au = LocalDate.parse("2026-10-15");
        when(service.devenir(eq(du), eq(au), isNull())).thenReturn(
                new DevenirInscriptions("Ensemble du Togo", du, au, 1000, 933, 40, 1, 26, 0));

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
    void uneZoneHorsPorteeEstRefusee() throws Exception {
        when(service.devenir(any(), any(), eq("SAV"))).thenThrow(new AccessDeniedException("hors portée"));
        mvc.perform(get("/api/v1/enrolement/devenir").param("zone", "SAV"))
                .andExpect(status().isForbidden());
    }
}
