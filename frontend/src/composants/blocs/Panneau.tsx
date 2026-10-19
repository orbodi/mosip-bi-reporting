import type { ReactNode } from 'react';
import './blocs.css';

interface Props {
  /** Identifiant du titre (aria-labelledby de la section). */
  id: string;
  titre: ReactNode;
  sousTitre?: ReactNode;
  /** Ligne au-dessus du titre (fil d'Ariane). */
  surTitre?: ReactNode;
  /** Contenu à droite de l'en-tête (légende, lien, chiffre clé). */
  aside?: ReactNode;
  /** Pastille de portée à côté du titre (« Ensemble du Togo »). */
  pastille?: ReactNode;
  /** Crochets jaunes aux quatre coins : élément principal de la page (maquette). */
  coins?: boolean;
  /** Le contenu gère lui-même ses marges (blocs « grand chiffre + cartes »). */
  sansMarge?: boolean;
  sansFilet?: boolean;
  className?: string;
  children: ReactNode;
}

/** Panneau de la maquette : en-tête (titre, sous-titre, aside) séparé du corps par un filet. */
export function Panneau({
  id,
  titre,
  sousTitre,
  surTitre,
  aside,
  pastille,
  coins,
  sansMarge,
  sansFilet,
  className = '',
  children,
}: Props) {
  return (
    <section className={`panneau-m ${className}`} aria-labelledby={id}>
      {coins && (
        <>
          <span className="coin coin--hg" aria-hidden="true" />
          <span className="coin coin--hd" aria-hidden="true" />
          <span className="coin coin--bg" aria-hidden="true" />
          <span className="coin coin--bd" aria-hidden="true" />
        </>
      )}
      <div className={`panneau-m__entete${sansFilet ? ' panneau-m__entete--sans-filet' : ''}`}>
        <div className="panneau-m__titres">
          {surTitre && <div className="panneau-m__sur-titre">{surTitre}</div>}
          <div className="panneau-m__ligne-titre">
            <h2 id={id} className="panneau-m__titre">
              {titre}
            </h2>
            {pastille}
          </div>
          {sousTitre && <p className="panneau-m__sous-titre">{sousTitre}</p>}
        </div>
        {aside}
      </div>
      {sansMarge ? children : <div className="panneau-m__corps">{children}</div>}
    </section>
  );
}
