/** Fraîcheur d'une source, telle que renvoyée par GET /api/v1/meta (bi.source_fraicheur). */
interface ChargementSource {
  source: string;
  dernierChargement?: string | null;
}

/**
 * Dernier rafraîchissement des chiffres d'une page : le chargement réussi le plus récent parmi les sources qu'elle
 * montre (le pipeline met à jour bi.source_fraicheur.dernier_chargement à chaque publication). Undefined si aucune
 * de ces sources n'a encore été chargée.
 */
export function dernierRafraichissement(sources: ChargementSource[], codes: string[]): string | undefined {
  return sources
    .filter((s) => codes.includes(s.source) && !!s.dernierChargement)
    .map((s) => s.dernierChargement as string)
    .reduce<string | undefined>(
      (plusRecent, d) => (!plusRecent || Date.parse(d) > Date.parse(plusRecent) ? d : plusRecent),
      undefined,
    );
}
