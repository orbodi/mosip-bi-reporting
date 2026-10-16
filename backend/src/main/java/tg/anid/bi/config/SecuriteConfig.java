package tg.anid.bi.config;

import java.util.List;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

/**
 * API sans état protégée par les jetons Keycloak (resource server OAuth2).
 * Rôles attendus : {@code bi-national} ou {@code bi-regional}. La portée géographique d'un utilisateur régional
 * est contrôlée dans chaque service, pas ici.
 */
@Configuration
public class SecuriteConfig {

    @Bean
    SecurityFilterChain filtres(HttpSecurity http, BiProprietes proprietes) throws Exception {
        http.csrf(csrf -> csrf.disable()) // jeton Bearer, pas de cookie de session
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .cors(Customizer.withDefaults());

        if (!proprietes.securite().active()) {
            // Profil dev uniquement (bi.securite.active=false).
            http.authorizeHttpRequests(a -> a.anyRequest().permitAll());
            return http.build();
        }

        http.authorizeHttpRequests(a -> a
                        .requestMatchers("/actuator/health/**", "/v3/api-docs/**", "/swagger-ui/**", "/swagger-ui.html")
                        .permitAll()
                        .requestMatchers("/api/**").hasAnyRole("BI_NATIONAL", "BI_REGIONAL")
                        .anyRequest().denyAll())
                .oauth2ResourceServer(o -> o.jwt(j -> j.jwtAuthenticationConverter(RolesKeycloak.convertisseur())));
        return http.build();
    }

    @Bean
    CorsConfigurationSource cors(BiProprietes proprietes) {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(proprietes.originesAutorisees());
        config.setAllowedMethods(List.of("GET", "OPTIONS"));
        config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
        config.setMaxAge(3600L);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", config);
        return source;
    }
}
