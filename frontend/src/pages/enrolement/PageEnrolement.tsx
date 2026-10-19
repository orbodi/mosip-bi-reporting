import { Link } from '@tanstack/react-router';
import { Bandeau } from '../../composants/coque/Bandeau';
import { FiltreRegion } from '../../composants/coque/FiltreRegion';
import type { DefinitionPage } from '../pages';
import { BlocAgeSexe } from './BlocAgeSexe';
import { BlocDevenir } from './BlocDevenir';
import { BlocPreinscription } from './BlocPreinscription';
import { BlocSemaines } from './BlocSemaines';
import { BlocTerritoire } from './BlocTerritoire';
import { BlocTopCentres } from './BlocTopCentres';

/** Page Enrôlement, dans l'ordre de la maquette (maquette/pages/Enrolement.dc.html). */
export function PageEnrolement({ page }: { page: DefinitionPage }) {
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
        <BlocPreinscription />
        <BlocDevenir />
        <BlocSemaines />
        <BlocTerritoire />
        <BlocAgeSexe />
        <BlocTopCentres />
      </div>
    </>
  );
}
