import { estConnu, largeurPyramide, type TrancheSexe } from '../../lib/blocsVides';
import { nf, part, pct } from '../../lib/format';
import './blocs.css';

const somme = (valeurs: number[]) => valeurs.reduce((a, v) => a + v, 0);

/**
 * Pyramide des âges (maquette Enrôlement, « NIU générés par âge et par sexe ») : femmes à gauche, hommes à droite,
 * tranches de la plus âgée à la plus jeune. Tableau ARIA : chaque tranche se lit « femmes, tranche, hommes ».
 * Valeur inconnue : 0 et piste grise à la place de la barre, jamais de forme estimée.
 */
export function Pyramide({ lignes, libelle }: { lignes: TrancheSexe[]; libelle: string }) {
  const femmes = somme(lignes.map((l) => l.femmes));
  const hommes = somme(lignes.map((l) => l.hommes));
  const total = femmes + hommes;

  const barre = (valeur: number, sexe: 'femmes' | 'hommes') => (
    <span
      className={`pyramide__barre pyramide__barre--${estConnu(valeur) ? sexe : 'vide'}`}
      style={{ width: `${estConnu(valeur) ? largeurPyramide(valeur, lignes) : 70}%` }}
    />
  );

  return (
    <div className="pyramide">
      <p className="pyramide__legende">
        <span className="pyramide__sexe pyramide__sexe--femmes">
          <i className="pyramide__puce pyramide__barre--femmes" aria-hidden="true" />
          <span>
            Femmes : <span className="chiffre">{nf(femmes)}</span> ({pct(part(femmes, total))})
          </span>
        </span>
        <span className="pyramide__sexe">
          <i className="pyramide__puce pyramide__barre--hommes" aria-hidden="true" />
          <span>
            Hommes : <span className="chiffre">{nf(hommes)}</span> ({pct(part(hommes, total))})
          </span>
        </span>
      </p>
      <div role="table" aria-label={libelle} className="pyramide__tableau">
        <div role="rowgroup" className="visuellement-cache">
          <div role="row">
            <span role="columnheader">Femmes</span>
            <span role="columnheader">Tranche d’âge</span>
            <span role="columnheader">Hommes</span>
          </div>
        </div>
        <div role="rowgroup" className="pyramide__lignes">
          {lignes.map((l) => (
            <div role="row" key={l.tranche} className="pyramide__ligne">
              <span role="cell" className="pyramide__cote pyramide__cote--femmes">
                <span className="chiffre pyramide__valeur">{nf(l.femmes)}</span>
                {barre(l.femmes, 'femmes')}
              </span>
              <span role="rowheader" className="pyramide__tranche">
                {l.tranche}
              </span>
              <span role="cell" className="pyramide__cote">
                {barre(l.hommes, 'hommes')}
                <span className="chiffre pyramide__valeur">{nf(l.hommes)}</span>
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
