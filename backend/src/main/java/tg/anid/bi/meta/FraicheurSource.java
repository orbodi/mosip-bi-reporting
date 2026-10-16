package tg.anid.bi.meta;

import java.time.LocalDate;
import java.time.OffsetDateTime;

/**
 * Fraîcheur d'une source de données du BI.
 *
 * @param source            code de la source (enrolement, cartes, abis, idps, authentifications)
 * @param libelle           libellé affiché
 * @param premiereDonnee    première date disponible (borne basse du filtre Période)
 * @param derniereDonnee    horodatage de la donnée la plus récente de la source
 * @param dernierChargement fin du dernier chargement réussi par le pipeline
 */
public record FraicheurSource(String source, String libelle, LocalDate premiereDonnee,
                              OffsetDateTime derniereDonnee, OffsetDateTime dernierChargement) {
}
