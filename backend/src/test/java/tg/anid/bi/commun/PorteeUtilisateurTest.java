package tg.anid.bi.commun;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.List;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;

class PorteeUtilisateurTest {

    private final PorteeUtilisateur portee = new PorteeUtilisateur();

    @AfterEach
    void nettoyer() {
        SecurityContextHolder.clearContext();
    }

    private static void connecter(String role, String zone) {
        Jwt.Builder jeton = Jwt.withTokenValue("jeton").header("alg", "none").claim("preferred_username", "agent");
        if (zone != null) {
            jeton.claim("zone", zone);
        }
        SecurityContextHolder.getContext().setAuthentication(
                new JwtAuthenticationToken(jeton.build(), List.of(new SimpleGrantedAuthority(role))));
    }

    @Test
    void sansJetonLaZoneDemandeeEstAppliquee() {
        assertThat(portee.zoneEffective(null)).isNull();
        assertThat(portee.zoneEffective(" ")).isNull();
        assertThat(portee.zoneEffective("SAV")).isEqualTo("SAV");
    }

    @Test
    void unUtilisateurNationalChoisitSaZone() {
        connecter("ROLE_BI_NATIONAL", null);
        assertThat(portee.zoneEffective(null)).isNull();
        assertThat(portee.zoneEffective("KAR")).isEqualTo("KAR");
    }

    @Test
    void unUtilisateurRegionalEstLimiteASaZone() {
        connecter("ROLE_BI_REGIONAL", "KAR");
        assertThat(portee.zoneEffective(null)).isEqualTo("KAR");
        assertThat(portee.zoneEffective("KAR")).isEqualTo("KAR");
        assertThatThrownBy(() -> portee.zoneEffective("SAV")).isInstanceOf(AccessDeniedException.class);
    }

    @Test
    void unUtilisateurRegionalSansZoneEstRefuse() {
        connecter("ROLE_BI_REGIONAL", null);
        assertThatThrownBy(() -> portee.zoneEffective(null)).isInstanceOf(AccessDeniedException.class);
    }
}
