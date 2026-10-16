package tg.anid.bi.commun;

import java.util.Optional;

import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Component;

/**
 * Portée géographique de l'utilisateur (règle de CLAUDE.md : appliquée par l'API, jamais seulement par le front).
 * Un utilisateur {@code bi-national} lit toutes les zones ; un {@code bi-regional} ne lit que la zone de son jeton
 * (claim {@code zone}, code de région). Sans jeton (profil dev, sécurité désactivée), aucune zone n'est imposée.
 */
@Component
public class PorteeUtilisateur {

    static final String CLAIM_ZONE = "zone";
    static final String ROLE_NATIONAL = "ROLE_BI_NATIONAL";

    /**
     * Zone à appliquer à une requête.
     *
     * @param zoneDemandee code de zone passé par le client, ou null / vide pour tout le périmètre autorisé
     * @return le code de zone à filtrer, ou null pour l'ensemble du Togo
     * @throws AccessDeniedException si un utilisateur régional demande une autre zone que la sienne
     */
    public String zoneEffective(String zoneDemandee) {
        String demandee = zoneDemandee == null || zoneDemandee.isBlank() ? null : zoneDemandee;
        Optional<String> imposee = zoneImposee(SecurityContextHolder.getContext().getAuthentication());
        if (imposee.isEmpty()) {
            return demandee;
        }
        if (demandee != null && !demandee.equals(imposee.get())) {
            throw new AccessDeniedException("Zone hors de la portée de l'utilisateur");
        }
        return imposee.get();
    }

    static Optional<String> zoneImposee(Authentication authentification) {
        if (authentification == null || !(authentification.getPrincipal() instanceof Jwt jeton)) {
            return Optional.empty();
        }
        boolean national = authentification.getAuthorities().stream()
                .anyMatch(autorite -> ROLE_NATIONAL.equals(autorite.getAuthority()));
        if (national) {
            return Optional.empty();
        }
        String zone = jeton.getClaimAsString(CLAIM_ZONE);
        if (zone == null || zone.isBlank()) {
            throw new AccessDeniedException("Utilisateur régional sans zone dans son jeton");
        }
        return Optional.of(zone);
    }
}
