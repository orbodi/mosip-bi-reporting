import { Link } from '@tanstack/react-router';

/**
 * Bandeau des pages de vue d'ensemble : lien vers l'Exploration, seule page à filtres (période, territoire). Avec
 * {@code source} (« auth », « abis »…), l'Exploration s'ouvre sur l'onglet de la page (05/11/2026).
 */
export function FiltresPage({ source }: { source?: string }) {
  return (
    <Link to="/exploration" search={source ? { source } : {}} className="lien-exploration">
      Filtres détaillés dans l’Exploration <span aria-hidden="true">→</span>
    </Link>
  );
}
