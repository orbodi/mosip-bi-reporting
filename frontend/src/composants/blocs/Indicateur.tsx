import { Link } from '@tanstack/react-router';
import type { ReactNode } from 'react';
import { classeCouleur, type Couleur } from './couleurs';
import { Icone } from './Icone';

interface Props {
  icone: string;
  nom: ReactNode;
  valeur: ReactNode;
  unite?: ReactNode;
  detail?: ReactNode;
  /** Pastille de couleur devant le nom (statut). */
  puce?: Couleur;
  /** Page liée (cartes « Indicateurs clés par module »). */
  lien?:
    '/' | '/enrolement' | '/impression-cartes' | '/abis' | '/idps' | '/authentifications' | '/exploration';
  taille?: 'normale' | 'grande' | 'module';
}

/** Carte d'indicateur à bordure jaune (maquette) : pictogramme, nom, nombre, détail. */
export function CarteIndicateur({
  icone,
  nom,
  valeur,
  unite,
  detail,
  puce,
  lien,
  taille = 'normale',
}: Props) {
  const corps = (
    <>
      <Icone nom={icone} />
      <div className="indicateur__corps">
        <span className="indicateur__nom">
          {puce && <i className={classeCouleur(puce)} aria-hidden="true" />}
          {nom}
        </span>
        <span className="indicateur__valeur chiffre">
          {valeur}
          {unite && <span className="indicateur__unite">{unite}</span>}
        </span>
        {detail && <span className="indicateur__detail">{detail}</span>}
      </div>
    </>
  );
  const classe = `indicateur indicateur--${taille}`;
  return lien ? (
    <Link to={lien} search={(precedent) => precedent} className={`${classe} indicateur--lien`}>
      {corps}
    </Link>
  ) : (
    <div className={classe}>{corps}</div>
  );
}

/** Grand chiffre d'un bloc (« 606 850 demandes de pré-enrôlement »). */
export function GrandChiffre({
  valeur,
  unite,
  detail,
}: {
  valeur: ReactNode;
  unite?: ReactNode;
  detail?: ReactNode;
}) {
  return (
    <div className="grand-chiffre">
      <p className="grand-chiffre__ligne">
        <span className="grand-chiffre__valeur chiffre">{valeur}</span>
        {unite && <span className="grand-chiffre__unite">{unite}</span>}
      </p>
      {detail && <p className="grand-chiffre__detail">{detail}</p>}
    </div>
  );
}
