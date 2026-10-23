import { Link } from '@tanstack/react-router';

/** Bandeau des pages de vue d'ensemble : lien vers l'Exploration, seule page à filtres (période, territoire). */
export function FiltresPage() {
  return (
    <Link to="/exploration" className="lien-exploration">
      Filtres détaillés dans l’Exploration <span aria-hidden="true">→</span>
    </Link>
  );
}
