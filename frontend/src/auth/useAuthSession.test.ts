import { act, cleanup, renderHook, waitFor } from '@testing-library/react'
import type { User } from 'oidc-client-ts'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { AuthService } from './authService.ts'
import { SESSION_EXPIRED_ERROR, useAuthSession } from './useAuthSession.ts'
import { notifySessionExpired } from './sessionExpiry.ts'

function makeUser(email = 'persona@example.test'): User {
  return { profile: { email } } as User
}

function createService(overrides: Partial<AuthService> = {}): AuthService {
  return {
    login: vi.fn(async () => {}),
    handleCallback: vi.fn(async () => null),
    getAccessToken: vi.fn(async () => null),
    getUser: vi.fn(async () => null),
    logout: vi.fn(async () => {}),
    clearSession: vi.fn(async () => {}),
    ...overrides,
  }
}

beforeEach(() => {
  window.history.replaceState(null, '', '/')
})

afterEach(() => {
  cleanup()
  window.history.replaceState(null, '', '/')
  vi.restoreAllMocks()
})

describe('useAuthSession con sesión caducada', () => {
  it('vuelve al login una sola vez y limpia la sesión', async () => {
    const service = createService({
      getUser: vi.fn(async () => makeUser()),
    })
    const { result } = renderHook(() => useAuthSession(service))

    await waitFor(() => expect(result.current.status).toBe('authenticated'))

    act(() => {
      notifySessionExpired()
    })

    await waitFor(() => expect(result.current.status).toBe('anonymous'))
    expect(result.current.email).toBeNull()
    expect(result.current.error).toBe(SESSION_EXPIRED_ERROR)
    expect(service.clearSession).toHaveBeenCalledTimes(1)
  })

  it('dos eventos concurrentes producen una sola limpieza', async () => {
    const service = createService({
      getUser: vi.fn(async () => makeUser()),
    })
    const { result } = renderHook(() => useAuthSession(service))

    await waitFor(() => expect(result.current.status).toBe('authenticated'))

    act(() => {
      notifySessionExpired()
      notifySessionExpired()
    })

    await waitFor(() => expect(result.current.status).toBe('anonymous'))
    expect(service.clearSession).toHaveBeenCalledTimes(1)
  })

  it('un getUser tardío no restaura la sesión', async () => {
    let resolveUser!: (user: User | null) => void
    const pendingUser = new Promise<User | null>((resolve) => {
      resolveUser = resolve
    })
    const service = createService({
      getUser: vi.fn(() => pendingUser),
    })
    const { result } = renderHook(() => useAuthSession(service))

    expect(result.current.status).toBe('checking')

    act(() => {
      notifySessionExpired()
    })

    expect(result.current.status).toBe('anonymous')

    await act(async () => {
      resolveUser(makeUser())
    })

    await waitFor(() => expect(result.current.status).toBe('anonymous'))
    expect(service.clearSession).toHaveBeenCalledTimes(1)
  })

  it('un login nuevo permite una transición posterior', async () => {
    const service = createService({
      getUser: vi.fn(async () => makeUser()),
    })
    const { result } = renderHook(() => useAuthSession(service))

    await waitFor(() => expect(result.current.status).toBe('authenticated'))

    act(() => {
      notifySessionExpired()
    })
    await waitFor(() => expect(result.current.status).toBe('anonymous'))
    expect(service.clearSession).toHaveBeenCalledTimes(1)

    await act(async () => {
      await result.current.signIn()
    })

    act(() => {
      notifySessionExpired()
    })

    await waitFor(() =>
      expect(service.clearSession).toHaveBeenCalledTimes(2),
    )
  })
})
