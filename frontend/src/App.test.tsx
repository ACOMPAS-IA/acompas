import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { User } from 'oidc-client-ts'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App.tsx'
import { DISCLAIMER_TEXT } from './components/disclaimer/Disclaimer.tsx'

const { authServiceMock } = vi.hoisted(() => ({
  authServiceMock: {
    login: vi.fn(),
    handleCallback: vi.fn(),
    getAccessToken: vi.fn(),
    getUser: vi.fn(),
    logout: vi.fn(),
  },
}))

vi.mock('./auth/authService.ts', () => ({
  authService: authServiceMock,
  isCallbackPath: () => false,
}))

const nowInSeconds = () => Math.floor(Date.now() / 1000)

function makeUser(email = 'persona@example.test'): User {
  const now = nowInSeconds()
  return new User({
    access_token: 'token-sintetico',
    token_type: 'Bearer',
    id_token: 'id-sintetico',
    refresh_token: 'refresh-sintetico',
    expires_at: now + 300,
    profile: {
      sub: 'persona-sintetica',
      iss: 'http://localhost:8080/realms/acompas',
      aud: 'acompas-frontend',
      exp: now + 300,
      iat: now,
      email,
    },
  })
}

beforeEach(() => {
  authServiceMock.login.mockResolvedValue(undefined)
  authServiceMock.handleCallback.mockResolvedValue(null)
  authServiceMock.getAccessToken.mockResolvedValue(null)
  authServiceMock.getUser.mockResolvedValue(null)
  authServiceMock.logout.mockResolvedValue(undefined)
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('App', () => {
  it('muestra el login cuando no hay sesión', async () => {
    render(<App />)

    expect(
      await screen.findByRole('heading', { name: 'Iniciar sesión' }),
    ).toBeDefined()
    expect(screen.queryByRole('navigation')).toBeNull()
    expect(authServiceMock.getUser).toHaveBeenCalled()
  })

  it('muestra el AppShell autenticado con email, logout y el aviso en el pie', async () => {
    authServiceMock.getUser.mockResolvedValue(makeUser())

    render(<App />)

    expect(
      await screen.findByRole('navigation', { name: 'Navegación principal' }),
    ).toBeDefined()
    expect(screen.getByRole('heading', { name: 'ACOMPAS' })).toBeDefined()
    expect(
      screen
        .getByRole('button', { name: 'Documento' })
        .getAttribute('aria-current'),
    ).toBe('page')
    expect(
      screen.getByRole('heading', { name: 'Subir documento' }),
    ).toBeDefined()
    expect(screen.queryByRole('button', { name: 'Conversación' })).toBeNull()
    expect(screen.getByRole('main')).toBeDefined()
    expect(screen.getByText('persona@example.test')).toBeDefined()
    expect(screen.getByRole('button', { name: 'Cerrar sesión' })).toBeDefined()

    const footer = screen.getByRole('contentinfo', { name: 'Aviso legal' })
    expect(within(footer).getByText(DISCLAIMER_TEXT)).toBeDefined()
  })

  it('vuelve al login al cerrar sesión', async () => {
    authServiceMock.getUser.mockResolvedValue(makeUser())

    render(<App />)

    fireEvent.click(await screen.findByRole('button', { name: 'Cerrar sesión' }))

    expect(
      await screen.findByRole('heading', { name: 'Iniciar sesión' }),
    ).toBeDefined()
    expect(authServiceMock.logout).toHaveBeenCalledTimes(1)
  })
})
