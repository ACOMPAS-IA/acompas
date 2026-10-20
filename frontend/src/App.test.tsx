import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import App from './App.tsx'

afterEach(cleanup)

describe('App', () => {
  it('monta AppShell con la conversación activa y contenido neutro', () => {
    render(<App />)

    expect(screen.getByRole('heading', { name: 'ACOMPAS' })).toBeDefined()
    expect(
      screen.getByRole('navigation', { name: 'Navegación principal' }),
    ).toBeDefined()
    expect(
      screen.getByRole('button', { name: 'Conversación' }).getAttribute('aria-current'),
    ).toBe('page')
    expect(screen.getByRole('main')).toBeDefined()
    expect(screen.getByText('Contenido de prueba')).toBeDefined()
    expect(
      screen.queryByRole('contentinfo', { name: 'Aviso legal' }),
    ).toBeNull()
  })
})
