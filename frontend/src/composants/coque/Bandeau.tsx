import type { ReactNode } from 'react';
import type { CodeSource } from '../../api/meta';
import { MiseAJour } from './MiseAJour';

interface Props {
  titre: string;
  source: CodeSource;
  /** Contenu sous le titre : lien vers l'Exploration (pages de vue d'ensemble). */
  filtres?: ReactNode;
  /** Texte d'introduction sous le titre (page Exploration). */
  chapeau?: ReactNode;
}

/**
 * Bandeau bleu en haut de chaque page : titre, date de mise à jour et lien vers l'Exploration. Les pages de vue
 * d'ensemble n'ont pas de filtre Période ni Région : filtres et exploration détaillée sont dans l'Exploration.
 * Le premier panneau chevauche le bandeau.
 */
export function Bandeau({ titre, source, filtres, chapeau }: Props) {
  return (
    <section className="bandeau" aria-labelledby="titre-page">
      <div className="bandeau__interieur">
        <div className="bandeau__ligne">
          <h1 id="titre-page" className="bandeau__titre">
            {titre}
          </h1>
          <MiseAJour source={source} />
        </div>
        {chapeau && <p className="bandeau__chapeau">{chapeau}</p>}
        {filtres && <div className="bandeau__filtres">{filtres}</div>}
      </div>
    </section>
  );
}
