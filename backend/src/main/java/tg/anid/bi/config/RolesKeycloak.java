package tg.anid.bi.config;

import java.util.Collection;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;

/**
 * Traduit les rôles du realm Keycloak (claim {@code realm_access.roles}) en rôles Spring Security.
 * Exemple : {@code bi-national} devient {@code ROLE_BI_NATIONAL}.
 */
public final class RolesKeycloak {

    private RolesKeycloak() {
    }

    public static JwtAuthenticationConverter convertisseur() {
        JwtAuthenticationConverter convertisseur = new JwtAuthenticationConverter();
        convertisseur.setJwtGrantedAuthoritiesConverter(RolesKeycloak::roles);
        convertisseur.setPrincipalClaimName("preferred_username");
        return convertisseur;
    }

    public static Collection<GrantedAuthority> roles(Jwt jwt) {
        Map<String, Object> realm = jwt.getClaimAsMap("realm_access");
        if (realm == null || !(realm.get("roles") instanceof Collection<?> roles)) {
            return List.of();
        }
        return roles.stream()
                .map(Object::toString)
                .map(role -> "ROLE_" + role.toUpperCase(Locale.ROOT).replace('-', '_'))
                .<GrantedAuthority>map(SimpleGrantedAuthority::new)
                .toList();
    }
}
