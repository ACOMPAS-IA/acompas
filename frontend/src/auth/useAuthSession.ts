import { useCallback, useEffect, useState } from 'react'
import { authService as defaultAuthService, isCallbackPath, type AuthService } from './authService.ts'

export const LOGIN_ERROR = 'No se ha podido iniciar la sesión. Inténtalo de nuevo.'
export const CALLBACK_ERROR =
  'No se ha podido completar el inicio de sesión. Inténtalo de nuevo.'
export const LOGOUT_ERROR = 'No se ha podido cerrar la sesión en Keycloak.'

export type AuthStatus = 'checking' | 'anonymous' | 'authenticated'

export type AuthSession = {
  status: AuthStatus
  email: string | null
  error: string | null
  redirecting: boolean
  signIn: () => Promise<void>
  signOut: () => Promise<void>
}

export function useAuthSession(
  service: AuthService = defaultAuthService,
): AuthSession {
  const [status, setStatus] = useState<AuthStatus>('checking')
  const [email, setEmail] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [redirecting, setRedirecting] = useState(false)

  useEffect(() => {
    let active = true

    async function bootstrap() {
      try {
        if (isCallbackPath()) {
          const user = await service.handleCallback()
          if (!active) return
          if (user) {
            setEmail(user.profile.email ?? null)
            setStatus('authenticated')
            return
          }
        }

        const user = await service.getUser()
        if (!active) return
        setEmail(user?.profile.email ?? null)
        setStatus(user ? 'authenticated' : 'anonymous')
      } catch {
        if (!active) return
        setError(CALLBACK_ERROR)
        setStatus('anonymous')
      }
    }

    void bootstrap()
    return () => {
      active = false
    }
  }, [service])

  const signIn = useCallback(async () => {
    setError(null)
    setRedirecting(true)
    try {
      await service.login()
    } catch {
      setError(LOGIN_ERROR)
      setRedirecting(false)
    }
  }, [service])

  const signOut = useCallback(async () => {
    setError(null)
    try {
      await service.logout()
    } catch {
      setError(LOGOUT_ERROR)
    } finally {
      // El logout elimina siempre la sesión local antes de redirigir.
      setStatus('anonymous')
      setEmail(null)
    }
  }, [service])

  return { status, email, error, redirecting, signIn, signOut }
}
