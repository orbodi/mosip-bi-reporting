import type { ReactNode } from 'react';

export interface LigneClassement {
  cle: string;
  nom: ReactNode;
  lieu?: ReactNode;
  valeur: ReactNode;
  detail?: ReactNode;
}

/** Tableau de classement de la maquette (rang, nom et lieu, valeur et détail). */
export function Classement({
  titre,
  colonneNom,
  colonneValeur,
  lignes,
}: {
  titre: string;
  colonneNom: string;
  colonneValeur: string;
  lignes: LigneClassement[];
}) {
  return (
    <table className="classement">
      <caption className="visuellement-cache">{titre}</caption>
      <thead>
        <tr>
          <th scope="col">Rang</th>
          <th scope="col">{colonneNom}</th>
          <th scope="col">{colonneValeur}</th>
        </tr>
      </thead>
      <tbody>
        {lignes.map((l, i) => (
          <tr key={l.cle}>
            <td className="classement__rang">{i + 1}</td>
            <th scope="row">
              <span className="classement__nom">{l.nom}</span>
              {l.lieu && <span className="classement__lieu">{l.lieu}</span>}
            </th>
            <td>
              <span className="classement__valeur chiffre">{l.valeur}</span>
              {l.detail && <span className="classement__detail">{l.detail}</span>}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
