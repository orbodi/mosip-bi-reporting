package tg.anid.bi.enrolement;

import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.time.OffsetDateTime;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import tg.anid.bi.commun.GestionErreurs;
import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.commun.RessourceIntrouvable;

class SuiviControllerTest {

    private static final String RID = "20101100230041220261021093015";

    private final SuiviService service = mock(SuiviService.class);
    private MockMvc mvc;

    @BeforeEach
    void preparer() {
        mvc = MockMvcBuilders.standaloneSetup(new SuiviController(service))
                .setControllerAdvice(new GestionErreurs())
                .build();
    }

    @Test
    void leRidVaDansLeCorpsEtNEstJamaisRenvoye() throws Exception {
        when(service.suivre(eq(RID))).thenReturn(new SuiviDossier("NEW", "niu", false,
                new SuiviDossier.Centre("EPP Doumassesse I G/B", "Golfe", "Grand Lomé"),
                new SuiviDossier.Etape("UIN_GENERATOR", "Génération du NIU", "SUCCESS"), null,
                OffsetDateTime.parse("2026-10-21T18:41:00Z"),
                new SuiviDossier.Jalons(OffsetDateTime.parse("2026-10-21T09:30:15Z"), null, false,
                        OffsetDateTime.parse("2026-10-21T10:16:00Z"), OffsetDateTime.parse("2026-10-21T18:40:00Z")),
                OffsetDateTime.parse("2026-10-26T09:55:00Z")));

        mvc.perform(post("/api/v1/enrolement/suivi").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"rid\":\"" + RID + "\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.devenir").value("niu"))
                .andExpect(jsonPath("$.centre.region").value("Grand Lomé"))
                .andExpect(jsonPath("$.jalons.niuLe").exists())
                .andExpect(jsonPath("$.rid").doesNotExist());
    }

    @Test
    void erreursFormatIntrouvableEtCorpsIllisible() throws Exception {
        when(service.suivre(eq("123"))).thenThrow(new RequeteInvalide("Le RID compte 29 chiffres."));
        when(service.suivre(eq(RID))).thenThrow(new RessourceIntrouvable(SuiviService.INTROUVABLE));

        mvc.perform(post("/api/v1/enrolement/suivi").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"rid\":\"123\"}"))
                .andExpect(status().isBadRequest());
        mvc.perform(post("/api/v1/enrolement/suivi").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"rid\":\"" + RID + "\"}"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.detail").value(SuiviService.INTROUVABLE));
        mvc.perform(post("/api/v1/enrolement/suivi").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"rid\": " + RID))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail").value("Le corps de la requête est illisible."));
    }
}
