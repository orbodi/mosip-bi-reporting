package tg.anid.bi.meta;

import static org.mockito.Mockito.mock;
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

class RegionsControllerTest {

    private final RegionsRepository repository = mock(RegionsRepository.class);
    private MockMvc mvc;

    @BeforeEach
    void preparer() {
        when(repository.regions()).thenReturn(List.of(new Region("SAV", "Savanes"), new Region("KAR", "Kara"),
                new Region("GLO", "Grand Lomé")));
        mvc = MockMvcBuilders.standaloneSetup(new RegionsController(repository))
                .setControllerAdvice(new GestionErreurs())
                .build();
    }

    @Test
    void renvoieToutesLesRegionsDansLOrdre() throws Exception {
        mvc.perform(get("/api/v1/meta/regions"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(3))
                .andExpect(jsonPath("$[0].code").value("SAV"))
                .andExpect(jsonPath("$[2].nom").value("Grand Lomé"));
    }
}
