// Configuración del cliente OIDC (ACO-013) para el login del frontend.
// Los valores fijos son los que el realm registra; solo el puerto de Keycloak
// es configurable, para que el login funcione con KEYCLOAK_PORT.

export const CALLBACK_PATH = '/auth/callback'
export const DEFAULT_KEYCLOAK_URL = 'http://localhost:8080'
export const FRONTEND_ORIGIN = 'http://localhost:5173'
export const CLIENT_ID = 'acompas-frontend'
export const SCOPE = 'openid profile email roles'

export type AuthConfig = {
  authority: string
  clientId: string
  redirectUri: string
  postLogoutRedirectUri: string
  scope: string
  callbackPath: string
}

function normalizeKeycloakUrl(value: string | undefined): string {
  const trimmed = value?.trim()
  const base = trimmed && trimmed.length > 0 ? trimmed : DEFAULT_KEYCLOAK_URL
  return base.replace(/\/+$/, '')
}

export function buildAuthConfig(keycloakUrl?: string): AuthConfig {
  return {
    authority: `${normalizeKeycloakUrl(keycloakUrl)}/realms/acompas`,
    clientId: CLIENT_ID,
    redirectUri: `${FRONTEND_ORIGIN}${CALLBACK_PATH}`,
    postLogoutRedirectUri: `${FRONTEND_ORIGIN}/`,
    scope: SCOPE,
    callbackPath: CALLBACK_PATH,
  }
}

// Vite 8 expone las variables VITE_* en import.meta.env; docker-compose pasa
// VITE_KEYCLOAK_URL con el puerto configurado de Keycloak.
export const authConfig = buildAuthConfig(import.meta.env.VITE_KEYCLOAK_URL)
