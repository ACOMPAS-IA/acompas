import {
  UserManager,
  WebStorageStateStore,
  type SignoutRedirectArgs,
  type User,
  type UserManagerSettings,
} from 'oidc-client-ts'
import { authConfig, type AuthConfig } from './authConfig.ts'

// Margen de renovación (D2): si al token le quedan 30 s o menos, se renueva
// bajo demanda con el refresh token.
export const EXPIRY_MARGIN_SECONDS = 30

export type AuthManager = {
  signinRedirect: () => Promise<void>
  signinRedirectCallback: (url?: string) => Promise<User>
  signinSilent: () => Promise<User | null>
  signoutRedirect: (args?: SignoutRedirectArgs) => Promise<void>
  getUser: () => Promise<User | null>
  removeUser: () => Promise<void>
}

export type AuthService = {
  login: () => Promise<void>
  handleCallback: (url?: string) => Promise<User | null>
  getAccessToken: () => Promise<string | null>
  getUser: () => Promise<User | null>
  logout: () => Promise<void>
}

export function buildUserManagerSettings(
  config: AuthConfig = authConfig,
): UserManagerSettings {
  return {
    authority: config.authority,
    client_id: config.clientId,
    redirect_uri: config.redirectUri,
    post_logout_redirect_uri: config.postLogoutRedirectUri,
    response_type: 'code',
    scope: config.scope,
    // Los tokens viven solo en la pestaña (P4); nunca en localStorage.
    userStore: new WebStorageStateStore({ store: window.sessionStorage }),
    stateStore: new WebStorageStateStore({ store: window.sessionStorage }),
    // Sin iframe ni renovación en segundo plano (P3).
    automaticSilentRenew: false,
    monitorSession: false,
  }
}

export function createUserManager(config: AuthConfig = authConfig): UserManager {
  return new UserManager(buildUserManagerSettings(config))
}

export function isCallbackPath(
  pathname: string = window.location.pathname,
  callbackPath: string = authConfig.callbackPath,
): boolean {
  return pathname === callbackPath
}

function cleanCallbackUrl(callbackPath: string): void {
  if (window.location.pathname !== callbackPath) return
  window.history.replaceState(null, '', '/')
}

function millisecondsLeft(user: User): number {
  if (typeof user.expires_at !== 'number') return 0
  return (user.expires_at - Date.now() / 1000) * 1000
}

export function createAuthService(
  manager: AuthManager,
  config: AuthConfig = authConfig,
): AuthService {
  // La guardia del callback se memoiza por URL en el servicio (P2): dos
  // efectos de StrictMode o un remontaje reutilizan la misma promesa y no
  // canjean el código dos veces.
  let pendingCallback: { url: string; promise: Promise<User> } | undefined

  async function handleCallback(url: string = window.location.href): Promise<User | null> {
    if (!pendingCallback || pendingCallback.url !== url) {
      pendingCallback = { url, promise: manager.signinRedirectCallback(url) }
    }

    try {
      return await pendingCallback.promise
    } finally {
      cleanCallbackUrl(config.callbackPath)
    }
  }

  async function login(): Promise<void> {
    await manager.signinRedirect()
  }

  async function getUser(): Promise<User | null> {
    return manager.getUser()
  }

  async function getAccessToken(): Promise<string | null> {
    const user = await manager.getUser()
    if (!user) return null

    if (millisecondsLeft(user) > EXPIRY_MARGIN_SECONDS * 1000) {
      return user.access_token
    }

    if (!user.refresh_token) {
      await manager.removeUser()
      return null
    }

    try {
      const renewed = await manager.signinSilent()
      if (!renewed?.access_token) {
        await manager.removeUser()
        return null
      }
      return renewed.access_token
    } catch {
      await manager.removeUser()
      return null
    }
  }

  async function logout(): Promise<void> {
    const user = await manager.getUser()
    const idTokenHint = user?.id_token

    // La sesión local se elimina antes de redirigir: así el cierre se
    // mantiene aunque la navegación interrumpa la promesa (P3).
    await manager.removeUser()
    await manager.signoutRedirect({
      id_token_hint: idTokenHint,
      post_logout_redirect_uri: config.postLogoutRedirectUri,
    })
  }

  return { login, handleCallback, getAccessToken, getUser, logout }
}

export const authService = createAuthService(createUserManager())

// Contrato con ACO-019: se llama antes de cada petición al API y null
// significa sesión no válida (volver al login).
export const getAccessToken = (): Promise<string | null> =>
  authService.getAccessToken()
