package tg.anid.bi.config;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;

class RolesKeycloakTest {

    private static Jwt jeton(Map<String, Object> claims) {
        Jwt.Builder builder = Jwt.withTokenValue("jeton-de-test").header("alg", "none").subject("agent-1");
        claims.forEach(builder::claim);
        return builder.build();
    }

    @Test
    void traduitLesRolesDuRealmEnRolesSpring() {
        Jwt jwt = jeton(Map.of("realm_access", Map.of("roles", List.of("bi-national", "offline_access"))));

        assertThat(RolesKeycloak.roles(jwt))
                .extracting(GrantedAuthority::getAuthority)
                .containsExactly("ROLE_BI_NATIONAL", "ROLE_OFFLINE_ACCESS");
    }

    @Test
    void sansRealmAccessAucunRole() {
        assertThat(RolesKeycloak.roles(jeton(Map.of("scope", "openid")))).isEmpty();
    }
}
