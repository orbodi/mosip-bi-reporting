package tg.anid.bi.meta;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import tg.anid.bi.commun.GestionErreurs;
import tg.anid.bi.commun.PorteeUtilisateur;

class RegionsControllerTest {

    private final RegionsRepository repository = mock(RegionsRepository.class);
    private MockMvc mvc;

    @BeforeEach
    void preparer() {
        when(repository.regions()).thenReturn(List.of(new Region("SAV", "Savanes"), new Region("KAR", "Kara"),
                new Region("GLO", "Grand Lomé")));
        mvc = MockMvcBuilders.standaloneSetup(new RegionsController(repository, new PorteeUtilisateur()))
                .setControllerAdvice(new GestionErreurs())
                .build();
    }

    @AfterEach
    void nettoyer() {
        SecurityContextHolder.clearContext();
    }

    private static void connecter(String role, String zone) {
        Jwt.Builder jeton = Jwt.withTokenValue("jeton").header("alg", "none").subject("agent");
        if (zone != null) {
            jeton.claim("zone", zone);
        }
        SecurityContextHolder.getContext().setAuthentication(
                new JwtAuthenticationToken(jeton.build(), List.of(new SimpleGrantedAuthority(role))));
    }

    @Test
    void unUtilisateurNationalVoitToutesLesRegionsDansLOrdre() throws Exception {
        connecter("ROLE_BI_NATIONAL", null);

        mvc.perform(get("/api/v1/meta/regions"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(3))
                .andExpect(jsonPath("$[0].code").value("SAV"))
                .andExpect(jsonPath("$[2].nom").value("Grand Lomé"));
    }

    @Test
    void unUtilisateurRegionalNeVoitQueSaRegion() throws Exception {
        connecter("ROLE_BI_REGIONAL", "KAR");

        mvc.perform(get("/api/v1/meta/regions"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(1))
                .andExpect(jsonPath("$[0].code").value("KAR"));
    }

    @Test
    void unUtilisateurRegionalSansZoneEstRefuse() throws Exception {
        connecter("ROLE_BI_REGIONAL", null);

        mvc.perform(get("/api/v1/meta/regions")).andExpect(status().isForbidden());
    }
}
