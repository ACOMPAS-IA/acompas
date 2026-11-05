import { AuthShell } from '../components/layout/AuthShell.tsx'

export type LoginPageProps = {
  error: string | null
  redirecting: boolean
  onSignIn: () => void
}

export function LoginPage({ error, redirecting, onSignIn }: LoginPageProps) {
  return (
    <AuthShell>
      <div className="login">
        <h2 className="login__title">Iniciar sesión</h2>
        <p className="login__text">
          Accede con tu cuenta para usar ACOMPAS.
        </p>
        {error ? (
          <p className="login__error" role="alert">
            {error}
          </p>
        ) : null}
        <button
          type="button"
          className="login__button"
          onClick={onSignIn}
          disabled={redirecting}
          aria-busy={redirecting || undefined}
        >
          {redirecting ? 'Redirigiendo…' : 'Iniciar sesión'}
        </button>
      </div>
    </AuthShell>
  )
}
