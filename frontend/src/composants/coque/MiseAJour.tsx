import { useFraicheur, type CodeSource } from '../../api/meta';
import { miseAJourFr } from '../../lib/format';

/** Pastille jaune « Dernière mise à jour : 14/01/2026 à 11h59 » (heure de la dernière donnée de la source). */
export function MiseAJour({ source }: { source: CodeSource }) {
  const { fraicheur, isPending, isError } = useFraicheur(source);
  let texte = isError ? 'Dernière mise à jour : –' : 'Dernière mise à jour : …';
  if (!isError && !isPending && fraicheur?.derniereDonnee)
    texte = `Dernière mise à jour : ${miseAJourFr(fraicheur.derniereDonnee)}`;

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
