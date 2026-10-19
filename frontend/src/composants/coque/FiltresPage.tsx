import { Link } from '@tanstack/react-router';
import { FiltreRegion } from './FiltreRegion';

/** Filtres du bandeau après la Période : Région (pages qui la suivent) et lien vers l'Exploration (maquette). */
export function FiltresPage({ region = false }: { region?: boolean }) {
  return (
    <>
      {region && <FiltreRegion />}
      <Link to="/exploration" search={(precedent) => precedent} className="lien-exploration">
        Filtres détaillés dans l’Exploration <span aria-hidden="true">→</span>
      </Link>
    </>
  );
}
