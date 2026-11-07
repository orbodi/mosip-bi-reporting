package tg.anid.bi.enrolement;

import static org.hamcrest.Matchers.nullValue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import tg.anid.bi.commun.GestionErreurs;

class ExplorationEnrolementControllerTest {

    private final ExplorationEnrolementService service = mock(ExplorationEnrolementService.class);
    private MockMvc mvc;

    @BeforeEach
    void preparer() {
        mvc = MockMvcBuilders.standaloneSetup(new ExplorationEnrolementController(service))
                .setControllerAdvice(new GestionErreurs())
                .build();
    }

    @Test
    void renvoieLesLignesParTypeSansPreinscriptions() throws Exception {
        when(service.exploration(isNull(), isNull(), eq("SAV"), any(), eq("type"))).thenReturn(
                new ExplorationEnrolement("Savanes", "SAV", null, null, null, "type",
                        List.of(new ExplorationEnrolement.Ligne("NEW", "NEW", null, false, false,
                                new ExplorationEnrolement.Chiffres(17, 14, 2, 1, 0, null))),
                        new ExplorationEnrolement.Chiffres(17, 14, 2, 1, 0, null), List.of(), List.of()));

        mvc.perform(get("/api/v1/enrolement/exploration").param("zone", "SAV").param("par", "type"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.lignes[0].cle").value("NEW"))
                .andExpect(jsonPath("$.lignes[0].chiffres.niuGeneres").value(14))
                .andExpect(jsonPath("$.total.preinscriptions").value(nullValue()));
    }

    @Test
    void transmetSexeTrancheEtNationaliteEtRefuseLesValeursInattendues() throws Exception {
        mvc.perform(get("/api/v1/enrolement/exploration").param("sexe", "F").param("age", "60+")
                        .param("nationalite", "TOGO").param("par", "nationalite"))
                .andExpect(status().isOk());
        verify(service).exploration(isNull(), isNull(), isNull(),
                eq(new ExplorationEnrolementRepository.Filtres(null, "F", "60+", "TOGO")), eq("nationalite"));

        mvc.perform(get("/api/v1/enrolement/exploration").param("sexe", "X"))
                .andExpect(status().isBadRequest());
        mvc.perform(get("/api/v1/enrolement/exploration").param("age", "18-25"))
                .andExpect(status().isBadRequest());
        mvc.perform(get("/api/v1/enrolement/exploration").param("par", "region"))
                .andExpect(status().isBadRequest());
    }
}
