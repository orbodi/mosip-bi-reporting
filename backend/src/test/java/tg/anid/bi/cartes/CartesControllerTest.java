package tg.anid.bi.cartes;

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

class CartesControllerTest {

    private final CartesService service = mock(CartesService.class);
    private MockMvc mvc;

    @BeforeEach
    void preparer() {
        mvc = MockMvcBuilders.standaloneSetup(new CartesController(service))
                .setControllerAdvice(new GestionErreurs())
                .build();
    }

    @Test
    void renvoieLImpressionEnNombresBruts() throws Exception {
        LocalDate du = LocalDate.parse("2026-10-01");
        LocalDate au = LocalDate.parse("2026-10-31");
        when(service.impression(eq(du), eq(au), isNull())).thenReturn(new ImpressionRemise("Ensemble du Togo", du, au,
                true, 6179588L, 6177214L, 2366L, 8L, 0L, 693L, LocalDate.parse("2026-03-13"), 6088392L, 4643515L,
                4446113L, 197370L, 32L, 0L, 1444877L, 34));

        mvc.perform(get("/api/v1/cartes/impression").param("du", "2026-10-01").param("au", "2026-10-31"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.disponible").value(true))
                .andExpect(jsonPath("$.demandes").value(6179588))
                .andExpect(jsonPath("$.enAttente").value(2366))
                .andExpect(jsonPath("$.annulees").value(693))
                .andExpect(jsonPath("$.derniereRejetee").value("2026-03-13"))
                .andExpect(jsonPath("$.remises").value(4643515))
                .andExpect(jsonPath("$.remisesEnLigne").value(197370))
                .andExpect(jsonPath("$.aRemettre").value(1444877))
                .andExpect(jsonPath("$.delaiMedianJours").value(34));
    }

    @Test
    void renvoieLAttenteEtLesAnnulations() throws Exception {
        when(service.attente(isNull(), isNull(), eq("SAV"))).thenReturn(new CartesEnAttente("Savanes", null, null,
                LocalDate.parse("2026-11-03"), 12, List.of(
                        new CartesEnAttente.Tranche("moins_30j", 0, 30, 2),
                        new CartesEnAttente.Tranche("plus_180j", 180, null, 10))));
        when(service.annulations(isNull(), isNull(), isNull())).thenReturn(new AnnulationsParMotif("Ensemble du Togo",
                null, null, 643, List.of(new AnnulationsParMotif.Motif("CANCEL_PHOTO", "Photo à reprendre", 643))));

        mvc.perform(get("/api/v1/cartes/attente").param("zone", "SAV"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.calculeLe").value("2026-11-03"))
                .andExpect(jsonPath("$.tranches[1].code").value("plus_180j"))
                .andExpect(jsonPath("$.tranches[1].avantJours").doesNotExist());
        mvc.perform(get("/api/v1/cartes/annulations"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.motifs[0].code").value("CANCEL_PHOTO"));
    }

    @Test
    void uneRequeteInvalideRepond400() throws Exception {
        when(service.semaines(eq(LocalDate.parse("2026-10-31")), eq(LocalDate.parse("2026-10-01")), isNull()))
                .thenThrow(new RequeteInvalide("La date « du » doit précéder la date « au »."));

        mvc.perform(get("/api/v1/cartes/semaines").param("du", "2026-10-31").param("au", "2026-10-01"))
                .andExpect(status().isBadRequest());
    }
}
