import { Outlet } from '@tanstack/react-router';
import { EnTete } from './EnTete';
import { PiedDePage } from './PiedDePage';
import './coque.css';

/** Mise en page commune : lien d'évitement, en-tête, contenu de la page, pied de page. */
export function Coque() {
  return (
    <div className="coque">
      <a href="#contenu" className="lien-evitement">
        Aller au contenu
      </a>
      <EnTete />
      <main id="contenu" tabIndex={-1}>
        <Outlet />
      </main>
      <PiedDePage />
    </div>
  );
}
