import type { ReactNode } from 'react';
import { classeCouleur, type Couleur } from './couleurs';

export interface Part {
  libelle: string;
  valeur: number;
  couleur: Couleur;
}

/**
 * Barre de répartition horizontale. Sans valeurs connues (NaN, API indisponible), la barre reste grise et
 * l'équivalent texte le dit.
 */
export function Repartition({ parts, libelle }: { parts: Part[]; libelle: string }) {
  const connues = parts.every((p) => Number.isFinite(p.valeur));
  const total = connues ? parts.reduce((t, p) => t + p.valeur, 0) : 0;
  return (
    <div className="repartition" role="img" aria-label={connues ? libelle : `${libelle} : non disponible`}>
      {total > 0 &&
        parts
          .filter((p) => p.valeur > 0)
          .map((p) => (
            <span
              key={p.libelle}
              className={classeCouleur(p.couleur)}
              style={{ flexGrow: p.valeur }}
              title={p.libelle}
            />
          ))}
    </div>
  );
}

export interface ElementLegende {
  libelle: string;
  couleur: Couleur;
  note?: ReactNode;
  /** Trait (courbe) plutôt que carré (barre). */
  ligne?: boolean;
}

export function Legende({ elements, libelle = 'Légende' }: { elements: ElementLegende[]; libelle?: string }) {
  return (
    <ul className="legende-m" aria-label={libelle}>
      {elements.map((e) => (
        <li key={e.libelle}>
          <i
            className={`${classeCouleur(e.couleur)}${e.ligne ? ' legende-m__ligne' : ''}`}
            aria-hidden="true"
          />
          {e.libelle}
          {e.note !== undefined && <strong>{e.note}</strong>}
        </li>
      ))}
    </ul>
  );
}

/** Petite jauge (part d'un maximum) ; vide quand la valeur est inconnue. */
export function Jauge({ valeur, max, couleur = 'bleu' }: { valeur: number; max: number; couleur?: Couleur }) {
  const largeur = Number.isFinite(valeur) && max > 0 ? Math.max(0, Math.min(100, (valeur / max) * 100)) : 0;
  return (
    <span className="jauge" aria-hidden="true">
      <span className={classeCouleur(couleur)} style={{ width: `${largeur}%` }} />
    </span>
  );
}
