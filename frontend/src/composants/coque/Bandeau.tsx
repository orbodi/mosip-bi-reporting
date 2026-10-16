import type { ReactNode } from 'react';
import type { CodeSource } from '../../api/meta';
import { FiltrePeriode } from './FiltrePeriode';
import { MiseAJour } from './MiseAJour';

interface Props {
  titre: string;
  source: CodeSource;
  sansPeriode?: boolean;
  /** Filtres propres à la page, après le filtre Période. */
  filtres?: ReactNode;
}

/** Bandeau bleu en haut de chaque page : titre, date de mise à jour, filtres. Le premier panneau le chevauche. */
export function Bandeau({ titre, source, sansPeriode, filtres }: Props) {
  return (
    <section className="bandeau" aria-labelledby="titre-page">
      <div className="bandeau__interieur">
        <div className="bandeau__ligne">
          <h1 id="titre-page" className="bandeau__titre">
            {titre}
          </h1>
          <MiseAJour source={source} />
        </div>
        {(!sansPeriode || filtres) && (
          <div className="bandeau__filtres">
            {!sansPeriode && <FiltrePeriode source={source} />}
            {filtres}
          </div>
        )}
      </div>
    </section>
  );
}
