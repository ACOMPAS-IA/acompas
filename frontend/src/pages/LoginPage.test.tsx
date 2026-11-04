import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { LoginPage } from './LoginPage.tsx'

afterEach(cleanup)

describe('LoginPage', () => {
  it('monta AuthShell con la marca, el título y un único botón', () => {
    const { container } = render(
      <LoginPage error={null} redirecting={false} onSignIn={() => {}} />,
    )

    expect(screen.getByRole('heading', { name: 'ACOMPAS' })).toBeDefined()
    expect(
      screen.getByRole('heading', { name: 'Iniciar sesión' }),
    ).toBeDefined()
    expect(screen.getAllByRole('button')).toHaveLength(1)
    expect(
      screen.getByRole('button', { name: 'Iniciar sesión' }),
    ).toBeDefined()
    expect(container.querySelector('input')).toBeNull()
    expect(container.querySelector('form')).toBeNull()
    expect(screen.queryByRole('navigation')).toBeNull()
    expect(screen.queryByRole('contentinfo')).toBeNull()
  })

  it('llama a onSignIn al pulsar el botón', () => {
    const onSignIn = vi.fn()

    render(<LoginPage error={null} redirecting={false} onSignIn={onSignIn} />)
    fireEvent.click(screen.getByRole('button', { name: 'Iniciar sesión' }))

    expect(onSignIn).toHaveBeenCalledTimes(1)
  })

  it('deshabilita el botón y lo marca ocupado mientras redirige', () => {
    render(<LoginPage error={null} redirecting onSignIn={() => {}} />)

    const button = screen.getByRole('button', { name: 'Redirigiendo…' })
    expect(button.hasAttribute('disabled')).toBe(true)
    expect(button.getAttribute('aria-busy')).toBe('true')
  })

  it('muestra el error con role alert sin ocultar el botón', () => {
    render(
      <LoginPage
        error="No se ha podido iniciar la sesión. Inténtalo de nuevo."
        redirecting={false}
        onSignIn={() => {}}
      />,
    )

    expect(screen.getByRole('alert').textContent).toBe(
      'No se ha podido iniciar la sesión. Inténtalo de nuevo.',
    )
    expect(
      screen.getByRole('button', { name: 'Iniciar sesión' }),
    ).toBeDefined()
  })
})
