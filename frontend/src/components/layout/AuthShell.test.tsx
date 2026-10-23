import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { AuthShell } from './AuthShell.tsx'

afterEach(cleanup)

describe('AuthShell', () => {
  it('renderiza la marca y el contenido sin el marco autenticado', () => {
    render(
      <AuthShell>
        <p>Formulario</p>
      </AuthShell>,
    )

    expect(screen.getByRole('main')).toBeDefined()
    expect(screen.getByRole('heading', { name: 'ACOMPAS' })).toBeDefined()
    expect(screen.getByText('Formulario')).toBeDefined()
    expect(screen.queryByRole('banner')).toBeNull()
    expect(screen.queryByRole('navigation')).toBeNull()
    expect(screen.queryByRole('contentinfo')).toBeNull()
  })
})
