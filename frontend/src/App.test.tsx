import { cleanup, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import App from './App.tsx'
import { DISCLAIMER_TEXT } from './components/disclaimer/Disclaimer.tsx'

afterEach(cleanup)

describe('App', () => {
  it('monta AppShell con la conversación activa, contenido neutro y el aviso en el pie', () => {
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

    const footer = screen.getByRole('contentinfo', { name: 'Aviso legal' })
    expect(within(footer).getByText(DISCLAIMER_TEXT)).toBeDefined()
  })
})
