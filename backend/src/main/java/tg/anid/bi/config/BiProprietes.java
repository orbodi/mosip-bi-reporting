package tg.anid.bi.config;

import java.util.List;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Réglages propres au BI (préfixe {@code bi}).
 *
 * @param securite           contrôle des jetons Keycloak ; désactivable en développement seulement
 * @param originesAutorisees origines autorisées à appeler l'API depuis un navigateur (CORS)
 * @param suivi              suivi d'un dossier : clé de l'empreinte du RID
 */
@ConfigurationProperties("bi")
public record BiProprietes(Securite securite, List<String> originesAutorisees, Suivi suivi) {

    public BiProprietes {
        securite = securite == null ? new Securite(true) : securite;
        originesAutorisees = originesAutorisees == null ? List.of() : List.copyOf(originesAutorisees);
        suivi = suivi == null ? new Suivi(null) : suivi;
    }

    public record Securite(boolean active) {
    }

    /**
     * Suivi d'un dossier.
     *
     * @param cle clé HMAC de l'empreinte du RID ({@code SUIVI_HMAC_CLE} de mosip-cdc/compose/.env), la même que celle
     *            de la publication de bi.suivi_dossier ; vide = suivi indisponible
     */
    public record Suivi(String cle) {

        /** Jamais la clé dans un journal ni un message d'erreur. */
        @Override
        public String toString() {
            return "Suivi[cle=" + (cle == null || cle.isBlank() ? "absente" : "***") + "]";
        }
    }
}
