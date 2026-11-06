import { useCallback, useEffect, useRef, useState } from 'react'
import { authService as defaultAuthService, isCallbackPath, type AuthService } from './authService.ts'
import { SESSION_EXPIRED_EVENT } from './sessionExpiry.ts'

export const LOGIN_ERROR = 'No se ha podido iniciar la sesión. Inténtalo de nuevo.'
export const CALLBACK_ERROR =
  'No se ha podido completar el inicio de sesión. Inténtalo de nuevo.'
export const LOGOUT_ERROR = 'No se ha podido cerrar la sesión en Keycloak.'
export const SESSION_EXPIRED_ERROR =
  'La sesión ha caducado. Vuelve a iniciar sesión.'

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
  const expiryHandled = useRef(false)
  const generation = useRef(0)

  // Una sola transición por sesión: los 401 concurrentes pueden emitir varios
  // eventos, pero solo el primero limpia la sesión y cambia el estado.
  useEffect(() => {
    function handleSessionExpired() {
      if (expiryHandled.current) return
      expiryHandled.current = true
      // Se invalida antes de cualquier await que pudiera restaurar la sesión.
      generation.current += 1
      setError(SESSION_EXPIRED_ERROR)
      setStatus('anonymous')
      setEmail(null)
      void service.clearSession().catch(() => {})
    }

    window.addEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired)
    return () => {
      window.removeEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired)
    }
  }, [service])

  useEffect(() => {
    let active = true
    const currentGeneration = generation.current

    const isCurrent = () =>
      active && generation.current === currentGeneration

    async function bootstrap() {
      try {
        if (isCallbackPath()) {
          const user = await service.handleCallback()
          if (!isCurrent()) return
          if (user) {
            // Un callback completado con éxito permite una nueva expiración.
            expiryHandled.current = false
            setEmail(user.profile.email ?? null)
            setStatus('authenticated')
            return
          }
        }

        const user = await service.getUser()
        if (!isCurrent()) return
        setEmail(user?.profile.email ?? null)
        setStatus(user ? 'authenticated' : 'anonymous')
      } catch {
        if (!isCurrent()) return
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
      // Solo un login completado con éxito rearma la transición.
      expiryHandled.current = false
    } catch {
      setError(LOGIN_ERROR)
      setRedirecting(false)
    }
  }, [service])

  const signOut = useCallback(async () => {
    // Invalida cualquier bootstrap pendiente antes de limpiar la sesión.
    generation.current += 1
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
