import { useEffect, useMemo, type ReactNode } from 'react';
import { AuthProvider, useAuth } from 'react-oidc-context';
import { definirFournisseurJeton } from '../api/client';
import {
  ContexteUtilisateur,
  UTILISATEUR_DEV,
  initiales,
  rolesDuJeton,
  type Utilisateur,
} from './utilisateur';

const ACTIVE = import.meta.env.VITE_AUTH_ACTIVE === 'true';
const KEYCLOAK = import.meta.env.VITE_KEYCLOAK_URL ?? 'http://localhost:8180';
const REALM = import.meta.env.VITE_KEYCLOAK_REALM ?? 'anid';
const CLIENT = import.meta.env.VITE_KEYCLOAK_CLIENT ?? 'bi-reporting';

/**
 * Connexion Keycloak (OIDC, code + PKCE). Désactivée par défaut en développement :
 * l'utilisateur est alors « Global admin, Niveau national » et l'API tourne sans sécurité (profil dev).
 */
export function Authentification({ children }: { children: ReactNode }) {
  if (!ACTIVE) {
    return <ContexteUtilisateur.Provider value={UTILISATEUR_DEV}>{children}</ContexteUtilisateur.Provider>;
  }
  return (
    <AuthProvider
      authority={`${KEYCLOAK}/realms/${REALM}`}
      client_id={CLIENT}
      redirect_uri={`${window.location.origin}/`}
      post_logout_redirect_uri={`${window.location.origin}/`}
      onSigninCallback={() => window.history.replaceState({}, document.title, window.location.pathname)}
    >
      <ExigerConnexion>{children}</ExigerConnexion>
    </AuthProvider>
  );
}

function ExigerConnexion({ children }: { children: ReactNode }) {
  const auth = useAuth();
  const jeton = auth.user?.access_token;

  useEffect(() => {
    definirFournisseurJeton(() => jeton);
  }, [jeton]);

  useEffect(() => {
    if (!auth.isLoading && !auth.isAuthenticated && !auth.activeNavigator && !auth.error) {
      void auth.signinRedirect();
    }
  }, [auth]);

  const utilisateur = useMemo<Utilisateur>(() => {
    const profil = auth.user?.profile;
    const nom = profil?.name ?? profil?.preferred_username ?? 'Utilisateur';
    const roles = rolesDuJeton(jeton);
    const zone = typeof profil?.zone === 'string' ? profil.zone : undefined;
    return {
      nom,
      initiales: initiales(nom),
      portee: roles.includes('bi-national') ? 'Niveau national' : (zone ?? 'Portée non définie'),
      roles,
    };
  }, [auth.user, jeton]);

  if (auth.error) {
    return <p role="alert">Connexion impossible : {auth.error.message}</p>;
  }
  if (!auth.isAuthenticated) {
    return <p aria-live="polite">Connexion en cours…</p>;
  }
  return <ContexteUtilisateur.Provider value={utilisateur}>{children}</ContexteUtilisateur.Provider>;
}
