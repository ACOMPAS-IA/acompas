import type { ReactNode } from 'react'
import './layout.css'

type NavItem = {
  id: string
  label: string
}

type AppShellProps = {
  navItems: NavItem[]
  activeNavId?: string
  onNavigate?: (id: string) => void
  account?: ReactNode
  disclaimer?: ReactNode
  children: ReactNode
}

export function AppShell({
  navItems,
  activeNavId,
  onNavigate,
  account,
  disclaimer,
  children,
}: AppShellProps) {
  return (
    <div className="app-shell">
      <header className="app-shell__header">
        <h1 className="app-shell__brand">ACOMPAS</h1>
        <div className="app-shell__account">{account}</div>
      </header>
      <nav className="app-shell__nav" aria-label="Navegación principal">
        {navItems.map((item) => (
          <button
            key={item.id}
            type="button"
            className="app-shell__nav-item"
            aria-current={item.id === activeNavId ? 'page' : undefined}
            onClick={() => onNavigate?.(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>
      <main className="app-shell__main">{children}</main>
      <footer
        className="app-shell__footer"
        aria-label="Aviso legal"
        hidden={!disclaimer}
      >
        {disclaimer}
      </footer>
    </div>
  )
}
