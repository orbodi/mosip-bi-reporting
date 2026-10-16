import { createContext, useContext } from 'react';

export interface Utilisateur {
  nom: string;
  initiales: string;
  /** « Niveau national » ou le nom de la zone d'un utilisateur régional. */
  portee: string;
  roles: string[];
}

export const UTILISATEUR_DEV: Utilisateur = {
  nom: 'Global admin',
  initiales: 'GA',
  portee: 'Niveau national',
  roles: ['bi-national'],
};

export const ContexteUtilisateur = createContext<Utilisateur>(UTILISATEUR_DEV);

export function useUtilisateur() {
  return useContext(ContexteUtilisateur);
}

export function initiales(nom: string): string {
  return (
    nom
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((mot) => mot[0]?.toUpperCase())
      .join('') || '?'
  );
}

/** Lit les rôles du realm dans la charge utile d'un jeton d'accès Keycloak (sans en vérifier la signature). */
export function rolesDuJeton(jeton: string | undefined): string[] {
  if (!jeton) return [];
  try {
    const charge = JSON.parse(atob(jeton.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))) as {
      realm_access?: { roles?: string[] };
    };
    return charge.realm_access?.roles ?? [];
  } catch {
    return [];
  }
}
