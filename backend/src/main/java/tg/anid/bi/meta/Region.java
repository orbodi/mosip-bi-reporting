package tg.anid.bi.meta;

/**
 * Une région du filtre Région (bandeau des pages).
 *
 * @param code code de la zone (bi.zone), passé à l'API dans le paramètre {@code zone}
 * @param nom  nom affiché
 */
public record Region(String code, String nom) {
}
