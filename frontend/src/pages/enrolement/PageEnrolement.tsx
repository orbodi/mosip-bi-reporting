import { Link } from '@tanstack/react-router';
import { Bandeau } from '../../composants/coque/Bandeau';
import { FiltreRegion } from '../../composants/coque/FiltreRegion';
import type { DefinitionPage } from '../pages';
import { BlocAgeSexe } from './BlocAgeSexe';
import { BlocDevenir } from './BlocDevenir';
import { BlocSemaines } from './BlocSemaines';
import { BlocTerritoire } from './BlocTerritoire';
import { BlocTopCentres } from './BlocTopCentres';

const BLOCS_FAITS = [
  'Devenir des inscriptions',
  'Inscriptions et NIU par semaine',
  'Territoire (carte et tableau des zones)',
  'Âge et sexe',
  'Top des centres',
];

/**
 * Page Enrôlement, dans l'ordre de la maquette. Reste à construire : « Pré-inscription », en attente de la décision
 * sur sa source (docs/plans/enrolement.md, P1).
 */
export function PageEnrolement({ page }: { page: DefinitionPage }) {
  const restants = page.blocs.filter((bloc) => !BLOCS_FAITS.includes(bloc));
  return (
    <>
      <Bandeau
        titre={page.titre}
        source={page.source}
        filtres={
          <>
            <FiltreRegion />
            <Link to="/exploration" search={(precedent) => precedent} className="lien-exploration">
              Filtres détaillés dans l’Exploration <span aria-hidden="true">→</span>
            </Link>
          </>
        }
      />
      <div className="contenu grille-page">
        <BlocDevenir />
        <BlocSemaines />
        <BlocTerritoire />
        <BlocAgeSexe />
        <BlocTopCentres />
        {restants.length > 0 && (
          <section className="panneau bloc-pleine-largeur" aria-labelledby="blocs-a-construire">
            <h2 id="blocs-a-construire" className="titre-bloc">
              Blocs à construire
            </h2>
            <p className="texte-2">
              Référence : <code>maquette/pages/{page.maquette}.dc.html</code>. Dans l’ordre de la maquette :
            </p>
            <ol>
              {restants.map((bloc) => (
                <li key={bloc}>{bloc}</li>
              ))}
            </ol>
          </section>
        )}
      </div>
    </>
  );
}
