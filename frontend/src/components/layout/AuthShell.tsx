import type { ReactNode } from 'react'
import './layout.css'

type AuthShellProps = {
  children: ReactNode
}

export function AuthShell({ children }: AuthShellProps) {
  return (
    <main className="auth-shell">
      <h1 className="auth-shell__brand">ACOMPAS</h1>
      <div className="auth-shell__content">{children}</div>
    </main>
  )
}
