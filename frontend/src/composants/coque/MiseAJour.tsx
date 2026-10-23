import { useMeta } from '../../api/meta';
import { dernierRafraichissement } from '../../lib/fraicheur';
import { miseAJourFr } from '../../lib/format';

/**
 * Pastille jaune « Dernière mise à jour : 23/10/2026 à 15h05 » : date et heure du dernier rafraîchissement des
 * chiffres de la page (chargement le plus récent du pipeline parmi ses sources). Relue avec la méta toutes les 30 s.
 */
export function MiseAJour({ sources }: { sources: string[] }) {
  const { data, isPending, isError } = useMeta();
  const dernier = data ? dernierRafraichissement(data.sources, sources) : undefined;
  let texte = isError ? 'Dernière mise à jour : –' : 'Dernière mise à jour : …';
  if (!isError && !isPending) texte = `Dernière mise à jour : ${dernier ? miseAJourFr(dernier) : '–'}`;

  return (
    <p className="mise-a-jour" aria-live="polite">
      <svg width="13" height="13" viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="9" />
        <polyline points="12 7 12 12 15 14" />
      </svg>
      {texte}
    </p>
  );
}
