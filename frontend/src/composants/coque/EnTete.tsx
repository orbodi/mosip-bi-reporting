import { Link } from '@tanstack/react-router';
import logo from '../../assets/anid-logo.svg';
import { useUtilisateur } from '../../auth/utilisateur';
import { PAGES } from '../../pages/pages';

function LiensNavigation({ classe }: { classe: string }) {
  return (
    <nav aria-label="Sections du tableau de bord" className={classe}>
      {PAGES.map((page) => (
        <Link
          key={page.chemin}
          to={page.chemin}
          search={(precedent) => precedent}
          activeOptions={{ exact: true, includeSearch: false }}
          className="en-tete__lien"
        >
          {page.onglet}
        </Link>
      ))}
    </nav>
  );
}

export function EnTete() {
  const utilisateur = useUtilisateur();
  return (
    <header className="en-tete">
      <div className="en-tete__interieur">
        <div className="en-tete__marque">
          <img src={logo} alt="ANID, Agence nationale d'identification" className="en-tete__logo" />
          <span className="en-tete__app">BI Reporting</span>
        </div>
        <LiensNavigation classe="en-tete__nav" />
        <details className="en-tete__menu">
          <summary>
            Menu
            <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </summary>
          <LiensNavigation classe="en-tete__nav-mobile" />
        </details>
        <div className="en-tete__utilisateur">
          <span aria-hidden="true" className="en-tete__avatar">
            {utilisateur.initiales}
          </span>
          <span className="en-tete__identite">
            <span className="en-tete__nom">{utilisateur.nom}</span>
            <span className="en-tete__portee">{utilisateur.portee}</span>
          </span>
        </div>
      </div>
    </header>
  );
}
