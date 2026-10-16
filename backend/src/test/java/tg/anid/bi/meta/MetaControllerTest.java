package tg.anid.bi.meta;

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

class MetaControllerTest {

    private final MetaRepository repository = mock(MetaRepository.class);
    private MockMvc mvc;

    @BeforeEach
    void preparer() {
        mvc = MockMvcBuilders.standaloneSetup(new MetaController(repository)).build();
    }

    @Test
    void renvoieLaFraicheurDesSourcesDansLOrdre() throws Exception {
        when(repository.fraicheurs()).thenReturn(List.of(
                new FraicheurSource("enrolement", "Enrôlement", LocalDate.parse("2024-01-01"),
                        OffsetDateTime.parse("2026-01-14T11:42:00Z"), null),
                new FraicheurSource("idps", "IDPS", LocalDate.parse("2026-07-03"), OffsetDateTime.parse("2026-07-03T17:09:00Z"), null)));

        mvc.perform(get("/api/v1/meta"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.application").value("BI Reporting ANID"))
                .andExpect(jsonPath("$.sources.length()").value(2))
                .andExpect(jsonPath("$.sources[0].source").value("enrolement"))
                .andExpect(jsonPath("$.sources[1].libelle").value("IDPS"));
    }
}
