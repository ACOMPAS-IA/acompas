import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AppShell } from './AppShell.tsx'

afterEach(cleanup)

const navItems = [
  { id: 'conversation', label: 'Conversación' },
  { id: 'history', label: 'Historial' },
]

describe('AppShell', () => {
  it('renderiza las regiones y los slots', () => {
    render(
      <AppShell
        navItems={navItems}
        activeNavId="conversation"
        account={<span>Cuenta</span>}
        disclaimer={<span>Aviso legal</span>}
      >
        <p>Contenido</p>
      </AppShell>,
    )

    expect(screen.getByRole('banner')).toBeDefined()
    expect(screen.getByRole('heading', { name: 'ACOMPAS' })).toBeDefined()
    expect(screen.getByText('Cuenta')).toBeDefined()
    expect(
      screen.getByRole('navigation', { name: 'Navegación principal' }),
    ).toBeDefined()
    expect(screen.getByRole('main')).toBeDefined()
    expect(screen.getByText('Contenido')).toBeDefined()
    expect(
      screen.getByRole('contentinfo', { name: 'Aviso legal' }),
    ).toBeDefined()
    expect(screen.getByText('Aviso legal')).toBeDefined()
  })

  it('no muestra el pie si no hay disclaimer', () => {
    render(
      <AppShell navItems={navItems} activeNavId="conversation">
        <p>Contenido</p>
      </AppShell>,
    )

    expect(screen.queryByRole('contentinfo')).toBeNull()
  })

  it('marca el ítem activo y entrega su id al navegar', () => {
    const onNavigate = vi.fn()

    render(
      <AppShell
        navItems={navItems}
        activeNavId="conversation"
        onNavigate={onNavigate}
      >
        <p>Contenido</p>
      </AppShell>,
    )

    const activeItem = screen.getByRole('button', { name: 'Conversación' })
    const inactiveItem = screen.getByRole('button', { name: 'Historial' })

    expect(activeItem.getAttribute('aria-current')).toBe('page')
    expect(inactiveItem.getAttribute('aria-current')).toBeNull()

    fireEvent.click(inactiveItem)

    expect(onNavigate).toHaveBeenCalledWith('history')
  })

  it('muestra los ítems y no falla cuando onNavigate se omite', () => {
    render(
      <AppShell navItems={navItems} activeNavId="conversation">
        <p>Contenido</p>
      </AppShell>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Historial' }))

    expect(screen.getByText('Contenido')).toBeDefined()
    expect(screen.getByRole('button', { name: 'Historial' })).toBeDefined()
  })

  it('no marca ningún ítem si activeNavId no coincide', () => {
    render(
      <AppShell navItems={navItems} activeNavId="unknown">
        <p>Contenido</p>
      </AppShell>,
    )

    expect(
      screen.getByRole('button', { name: 'Conversación' }).getAttribute('aria-current'),
    ).toBeNull()
    expect(
      screen.getByRole('button', { name: 'Historial' }).getAttribute('aria-current'),
    ).toBeNull()
  })
})
