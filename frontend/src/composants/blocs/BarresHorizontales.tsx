import { nf } from '../../lib/format';
import { classeCouleur, type Couleur } from './couleurs';

/** Barres horizontales (ancienneté, répartition) ; valeurs à 0 quand elles sont inconnues. */
export function BarresHorizontales({
  elements,
  libelle,
}: {
  elements: { libelle: string; valeur: number; couleur: Couleur }[];
  libelle: string;
}) {
  const max = Math.max(1, ...elements.map((e) => (Number.isFinite(e.valeur) ? e.valeur : 0)));
  return (
    <ul className="barres-h" aria-label={libelle}>
      {elements.map((e) => (
        <li key={e.libelle} className="barres-h__ligne">
          <span>{e.libelle}</span>
          <span className="barres-h__piste">
            <span
              className={`barres-h__barre ${classeCouleur(e.couleur)}`}
              style={{ width: `${Number.isFinite(e.valeur) ? (e.valeur / max) * 75 : 0}%` }}
            />
            <span className="barres-h__valeur chiffre">{nf(e.valeur)}</span>
          </span>
        </li>
      ))}
    </ul>
  );
}
