import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { DISCLAIMER_TEXT, Disclaimer } from './Disclaimer.tsx'

afterEach(cleanup)

describe('Disclaimer', () => {
  it('pinta el aviso exacto en un único párrafo sin elementos interactivos', () => {
    const { container } = render(<Disclaimer />)

    const paragraphs = container.querySelectorAll('p')
    expect(paragraphs).toHaveLength(1)

    const paragraph = paragraphs[0]
    expect(paragraph.textContent).toBe(DISCLAIMER_TEXT)
    expect(paragraph.className).toBe('disclaimer')
    expect(paragraph.children).toHaveLength(0)
    expect(screen.queryByRole('link')).toBeNull()
    expect(screen.queryByRole('button')).toBeNull()
  })

  it('el texto es el de la sección 8 y no pasa de 140 caracteres', () => {
    expect(DISCLAIMER_TEXT).toBe(
      'ACOMPAS te ayuda a entender tu documentación, pero no diagnostica ni sustituye al médico. Consulta siempre con tu equipo oncológico.',
    )
    expect(DISCLAIMER_TEXT.length).toBeLessThanOrEqual(140)
    expect(DISCLAIMER_TEXT).toContain('entender')
    expect(DISCLAIMER_TEXT).toContain('no diagnostica')
    expect(DISCLAIMER_TEXT).toContain('sustituye al médico')
    expect(DISCLAIMER_TEXT).toContain('equipo oncológico')
  })
})
