/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** « true » pour exiger la connexion Keycloak (désactivée par défaut en développement). */
  readonly VITE_AUTH_ACTIVE?: string;
  /** Ex. https://keycloak.anid.tg ou http://localhost:8180 */
  readonly VITE_KEYCLOAK_URL?: string;
  readonly VITE_KEYCLOAK_REALM?: string;
  readonly VITE_KEYCLOAK_CLIENT?: string;
  /** Base de l'API si elle n'est pas servie sur la même origine. */
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
