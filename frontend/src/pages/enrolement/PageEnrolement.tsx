import { Bandeau } from '../../composants/coque/Bandeau';
import { FiltresPage } from '../../composants/coque/FiltresPage';
import type { DefinitionPage } from '../pages';
import { BlocAgeSexe } from './BlocAgeSexe';
import { BlocArrets } from './BlocArrets';
import { BlocDelais } from './BlocDelais';
import { BlocDevenir } from './BlocDevenir';
import { BlocJours } from './BlocJours';
import { BlocPreinscription } from './BlocPreinscription';
import { BlocProfilPreinscription } from './BlocProfilPreinscription';
import { BlocTerritoire } from './BlocTerritoire';
import { BlocTopCentres } from './BlocTopCentres';

/**
 * Page Enrôlement, dans l'ordre de la maquette (maquette/pages/Enrolement.dc.html), avec les blocs du lot 5
 * (« Où s'arrêtent les paquets », « Délais de traitement ») après le Top des centres ; âge, sexe et nationalité des
 * NIU puis Top des centres, chacun sur toute la largeur (décisions du 28/10/2026).
 */
export function PageEnrolement({ page }: { page: DefinitionPage }) {
  return (
    <>
      <Bandeau
        titre={page.titre}
        source={page.source}
        sourcesMiseAJour={page.sourcesMiseAJour}
        filtres={<FiltresPage />}
      />
      <div className="contenu grille-page">
        <BlocPreinscription />
        <BlocProfilPreinscription />
        <BlocDevenir />
        <BlocJours />
        <BlocTerritoire />
        <BlocAgeSexe />
        <BlocTopCentres />
        <BlocArrets />
        <BlocDelais />
      </div>
    </>
  );
}
