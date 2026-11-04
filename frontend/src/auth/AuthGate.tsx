import { Disclaimer } from '../components/disclaimer/Disclaimer.tsx'
import { AppShell } from '../components/layout/AppShell.tsx'
import { AuthShell } from '../components/layout/AuthShell.tsx'
import { LoginPage } from '../pages/LoginPage.tsx'
import { useAuthSession } from './useAuthSession.ts'
import type { AuthService } from './authService.ts'
import './auth.css'

const navItems = [{ id: 'conversation', label: 'Conversación' }]

type AuthGateProps = {
  service?: AuthService
}

export function AuthGate({ service }: AuthGateProps) {
  const { status, email, error, redirecting, signIn, signOut } =
    useAuthSession(service)

  if (status === 'checking') {
    return (
      <AuthShell>
        <p className="auth-status" role="status">
          Comprobando sesión…
        </p>
      </AuthShell>
    )
  }

  if (status === 'anonymous') {
    return (
      <LoginPage
        error={error}
        redirecting={redirecting}
        onSignIn={() => void signIn()}
      />
    )
  }

  return (
    <AppShell
      navItems={navItems}
      activeNavId="conversation"
      disclaimer={<Disclaimer />}
      account={
        <div className="auth-account">
          <span className="auth-account__email">
            {email ?? 'Sesión iniciada'}
          </span>
          <button
            type="button"
            className="auth-account__logout"
            onClick={() => void signOut()}
          >
            Cerrar sesión
          </button>
        </div>
      }
    >
      <p>Contenido de prueba</p>
    </AppShell>
  )
}
