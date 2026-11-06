import { User } from 'oidc-client-ts'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { buildAuthConfig } from './authConfig.ts'
import {
  EXPIRY_MARGIN_SECONDS,
  createAuthService,
  isCallbackPath,
  type AuthManager,
} from './authService.ts'

const config = buildAuthConfig()

const nowInSeconds = () => Math.floor(Date.now() / 1000)

function makeUser(
  options: {
    accessToken?: string
    refreshToken?: string
    expiresInSeconds?: number
    email?: string
  } = {},
): User {
  const now = nowInSeconds()
  return new User({
    access_token: options.accessToken ?? 'token-sintetico',
    token_type: 'Bearer',
    id_token: 'id-sintetico',
    refresh_token: options.refreshToken,
    expires_at: now + (options.expiresInSeconds ?? 300),
    profile: {
      sub: 'persona-sintetica',
      iss: 'http://localhost:8080/realms/acompas',
      aud: 'acompas-frontend',
      exp: now + 300,
      iat: now,
      email: options.email ?? 'persona@example.test',
    },
  })
}

function createManager(overrides: Partial<AuthManager> = {}): AuthManager {
  return {
    signinRedirect: vi.fn(async () => {}),
    signinRedirectCallback: vi.fn(async () => makeUser()),
    signinSilent: vi.fn(async () => null),
    signoutRedirect: vi.fn(async () => {}),
    getUser: vi.fn(async () => null),
    removeUser: vi.fn(async () => {}),
    ...overrides,
  }
}

afterEach(() => {
  window.history.replaceState(null, '', '/')
  vi.restoreAllMocks()
})

describe('buildAuthConfig', () => {
  it('usa los valores de ACO-013 y el puerto por defecto de Keycloak', () => {
    expect(config).toEqual({
      authority: 'http://localhost:8080/realms/acompas',
      clientId: 'acompas-frontend',
      redirectUri: 'http://localhost:5173/auth/callback',
      postLogoutRedirectUri: 'http://localhost:5173/',
      scope: 'openid profile email roles',
      callbackPath: '/auth/callback',
    })
  })

  it('acepta un puerto distinto y normaliza las barras finales', () => {
    expect(buildAuthConfig('http://localhost:18080/').authority).toBe(
      'http://localhost:18080/realms/acompas',
    )
    expect(buildAuthConfig('  http://localhost:18080//  ').authority).toBe(
      'http://localhost:18080/realms/acompas',
    )
  })

  it('vuelve al valor por defecto si la variable está vacía', () => {
    expect(buildAuthConfig('').authority).toBe(
      'http://localhost:8080/realms/acompas',
    )
  })

  it('detecta solo la ruta de callback', () => {
    expect(isCallbackPath('/auth/callback')).toBe(true)
    expect(isCallbackPath('/')).toBe(false)
    expect(isCallbackPath('/auth/callback/extra')).toBe(false)
  })
})

describe('authentication service', () => {
  it('delega el inicio de sesión en signinRedirect', async () => {
    const signinRedirect = vi.fn(async () => {})
    const service = createAuthService(createManager({ signinRedirect }), config)

    await service.login()

    expect(signinRedirect).toHaveBeenCalledTimes(1)
  })

  it('deduplica el callback por URL y limpia la URL a /', async () => {
    window.history.replaceState(null, '', '/auth/callback?code=abc&state=xyz')
    const url = window.location.href
    const signinRedirectCallback = vi.fn(async () => makeUser())
    const service = createAuthService(
      createManager({ signinRedirectCallback }),
      config,
    )

    const [first, second] = await Promise.all([
      service.handleCallback(),
      service.handleCallback(),
    ])

    expect(signinRedirectCallback).toHaveBeenCalledTimes(1)
    expect(signinRedirectCallback).toHaveBeenCalledWith(url)
    expect(first).toBe(second)
    expect(window.location.pathname).toBe('/')
  })

  it('limpia la URL a / también cuando el callback falla', async () => {
    window.history.replaceState(null, '', '/auth/callback?code=abc&state=xyz')
    const signinRedirectCallback = vi.fn(async () => {
      throw new Error('callback inválido')
    })
    const service = createAuthService(
      createManager({ signinRedirectCallback }),
      config,
    )

    await expect(service.handleCallback()).rejects.toThrow('callback inválido')
    expect(window.location.pathname).toBe('/')
  })

  it('devuelve el token vigente sin renovar', async () => {
    const user = makeUser({ accessToken: 'token-vigente', expiresInSeconds: 300 })
    const signinSilent = vi.fn(async () => null)
    const service = createAuthService(
      createManager({ getUser: vi.fn(async () => user), signinSilent }),
      config,
    )

    await expect(service.getAccessToken()).resolves.toBe('token-vigente')
    expect(signinSilent).not.toHaveBeenCalled()
  })

  it('no renueva con 31 s de vida', async () => {
    const user = makeUser({ accessToken: 'token-31s', expiresInSeconds: 31 })
    const signinSilent = vi.fn(async () => null)
    const service = createAuthService(
      createManager({ getUser: vi.fn(async () => user), signinSilent }),
      config,
    )

    await expect(service.getAccessToken()).resolves.toBe('token-31s')
    expect(signinSilent).not.toHaveBeenCalled()
  })

  it('renueva con refresh token con 29 s de vida', async () => {
    const user = makeUser({ refreshToken: 'refresh-sintetico', expiresInSeconds: 29 })
    const renewed = makeUser({ accessToken: 'token-renovado' })
    const signinSilent = vi.fn(async () => renewed)
    const service = createAuthService(
      createManager({ getUser: vi.fn(async () => user), signinSilent }),
      config,
    )

    await expect(service.getAccessToken()).resolves.toBe('token-renovado')
    expect(signinSilent).toHaveBeenCalledTimes(1)
  })

  it('elimina la sesión y devuelve null si no hay refresh token', async () => {
    const user = makeUser({ expiresInSeconds: 29 })
    const removeUser = vi.fn(async () => {})
    const signinSilent = vi.fn(async () => null)
    const service = createAuthService(
      createManager({
        getUser: vi.fn(async () => user),
        removeUser,
        signinSilent,
      }),
      config,
    )

    await expect(service.getAccessToken()).resolves.toBeNull()
    expect(removeUser).toHaveBeenCalledTimes(1)
    expect(signinSilent).not.toHaveBeenCalled()
  })

  it('elimina la sesión y devuelve null si la renovación falla', async () => {
    const user = makeUser({ refreshToken: 'refresh-sintetico', expiresInSeconds: 29 })
    const removeUser = vi.fn(async () => {})
    const signinSilent = vi.fn(async () => {
      throw new Error('renovación fallida')
    })
    const service = createAuthService(
      createManager({
        getUser: vi.fn(async () => user),
        removeUser,
        signinSilent,
      }),
      config,
    )

    await expect(service.getAccessToken()).resolves.toBeNull()
    expect(removeUser).toHaveBeenCalledTimes(1)
  })

  it('elimina la sesión y devuelve null si no hay usuario', async () => {
    const service = createAuthService(createManager(), config)

    await expect(service.getAccessToken()).resolves.toBeNull()
  })

  it('elimina la sesión local antes de redirigir al logout', async () => {
    const user = makeUser({ expiresInSeconds: 300 })
    const removeUser = vi.fn(async () => {})
    const signoutRedirect = vi.fn(async () => {})
    const service = createAuthService(
      createManager({
        getUser: vi.fn(async () => user),
        removeUser,
        signoutRedirect,
      }),
      config,
    )

    await service.logout()

    expect(removeUser.mock.invocationCallOrder[0]).toBeLessThan(
      signoutRedirect.mock.invocationCallOrder[0],
    )
    expect(signoutRedirect).toHaveBeenCalledWith({
      id_token_hint: 'id-sintetico',
      post_logout_redirect_uri: 'http://localhost:5173/',
    })
  })

  it('clearSession elimina la sesión local sin redirigir', async () => {
    const removeUser = vi.fn(async () => {})
    const signoutRedirect = vi.fn(async () => {})
    const service = createAuthService(
      createManager({ removeUser, signoutRedirect }),
      config,
    )

    await service.clearSession()

    expect(removeUser).toHaveBeenCalledTimes(1)
    expect(signoutRedirect).not.toHaveBeenCalled()
  })
})

describe('margen de renovación', () => {
  it('es de 30 s', () => {
    expect(EXPIRY_MARGIN_SECONDS).toBe(30)
  })
})
