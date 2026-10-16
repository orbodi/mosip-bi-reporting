package tg.anid.bi.config;

import java.util.List;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Réglages propres au BI (préfixe {@code bi}).
 *
 * @param securite           contrôle des jetons Keycloak ; désactivable en développement seulement
 * @param originesAutorisees origines autorisées à appeler l'API depuis un navigateur (CORS)
 */
@ConfigurationProperties("bi")
public record BiProprietes(Securite securite, List<String> originesAutorisees) {

    public BiProprietes {
        securite = securite == null ? new Securite(true) : securite;
        originesAutorisees = originesAutorisees == null ? List.of() : List.copyOf(originesAutorisees);
    }

    public record Securite(boolean active) {
    }
}
