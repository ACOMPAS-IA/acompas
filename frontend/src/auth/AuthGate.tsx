import { useState } from 'react'
import type { AnonymizationResult } from '../api/anonymization.ts'
import { Disclaimer } from '../components/disclaimer/Disclaimer.tsx'
import { AppShell } from '../components/layout/AppShell.tsx'
import { AuthShell } from '../components/layout/AuthShell.tsx'
import { ConversationPage } from '../pages/ConversationPage.tsx'
import { LoginPage } from '../pages/LoginPage.tsx'
import { UploadPage } from '../pages/UploadPage.tsx'
import { ValidationResultPage } from '../pages/ValidationResultPage.tsx'
import { useAuthSession } from './useAuthSession.ts'
import type { AuthService } from './authService.ts'
import './auth.css'

type Screen = 'upload' | 'result' | 'conversation'

type AuthenticatedAppProps = {
  email: string | null
  onSignOut: () => void
}

// El estado del flujo vive aquí y se descarta al desmontar (logout o caducidad
// de sesión). No hay router ni almacenamiento.
function AuthenticatedApp({ email, onSignOut }: AuthenticatedAppProps) {
  const [screen, setScreen] = useState<Screen>('upload')
  const [result, setResult] = useState<AnonymizationResult | null>(null)

  const validated =
    result?.status === 'validado' && result.anonymized_text !== null

  // «Conversación» solo aparece cuando hay un documento validado y, por tanto,
  // es alcanzable (T-09, R-12). AppShell no tiene estado deshabilitado.
  const navItems = [{ id: 'document', label: 'Documento' }]
  if (validated) {
    navItems.push({ id: 'conversation', label: 'Conversación' })
  }

  const activeNavId = screen === 'conversation' ? 'conversation' : 'document'

  function handleNavigate(id: string) {
    if (id === 'conversation') {
      if (validated) setScreen('conversation')
      return
    }
    if (id === 'document') {
      // El resultado validado se conserva hasta que una nueva subida lo
      // sustituya; la conversación se desmonta y pierde su hilo.
      setScreen('upload')
    }
  }

  function handleResult(next: AnonymizationResult) {
    setResult(next)
    setScreen('result')
  }

  function handleRestart() {
    setResult(null)
    setScreen('upload')
  }

  function handleContinue() {
    if (result?.status === 'validado' && result.anonymized_text !== null) {
      setScreen('conversation')
    }
  }

  return (
    <AppShell
      navItems={navItems}
      activeNavId={activeNavId}
      onNavigate={handleNavigate}
      disclaimer={<Disclaimer />}
      account={
        <div className="auth-account">
          <span className="auth-account__email">
            {email ?? 'Sesión iniciada'}
          </span>
          <button
            type="button"
            className="auth-account__logout"
            onClick={onSignOut}
          >
            Cerrar sesión
          </button>
        </div>
      }
    >
      {screen === 'upload' && <UploadPage onResult={handleResult} />}
      {screen === 'result' && result && (
        <ValidationResultPage
          result={result}
          onContinue={handleContinue}
          onRestart={handleRestart}
        />
      )}
      {screen === 'conversation' && result?.anonymized_text != null && (
        <ConversationPage documents={[{ text: result.anonymized_text }]} />
      )}
    </AppShell>
  )
}

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

  return <AuthenticatedApp email={email} onSignOut={() => void signOut()} />
}
