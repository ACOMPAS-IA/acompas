import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { AnonymizationResult } from '../api/anonymization.ts'
import { ValidationResultPage } from './ValidationResultPage.tsx'

// Texto inventado con etiquetas de anonimización (ACO-032, sección 9).
const ANONYMIZED = 'Paciente: [PACIENTE]. DNI: [DNI].'
const ORIGINAL = 'Paciente: Juan Pérez. DNI: 12345678Z.'

const VALID: AnonymizationResult = {
  status: 'validado',
  confidence: 0.93,
  anonymized_text: ANONYMIZED,
  entities_count: { PERSON: 2, ES_DNI: 1 },
  reason: null,
}

const RETAINED: AnonymizationResult = {
  status: 'retenido',
  confidence: 0.42,
  anonymized_text: null,
  entities_count: { PERSON: 1 },
  reason: 'baja_confianza',
}

const ILLEGIBLE: AnonymizationResult = {
  status: 'ilegible',
  confidence: 1,
  anonymized_text: null,
  entities_count: {},
  reason: 'texto_vacio',
}

afterEach(cleanup)

function renderPage(result: AnonymizationResult) {
  const onContinue = vi.fn()
  const onRestart = vi.fn()
  const view = render(
    <ValidationResultPage
      result={result}
      onContinue={onContinue}
      onRestart={onRestart}
    />,
  )
  return { ...view, onContinue, onRestart }
}

describe('ValidationResultPage', () => {
  it('muestra confianza, entidades y texto anonimizado en validado', () => {
    const { container } = renderPage(VALID)

    expect(screen.getByRole('heading', { name: 'Documento validado' })).toBeDefined()
    expect(screen.getByText('Confianza del documento: 93,0 %')).toBeDefined()
    const entities = screen.getAllByRole('listitem').map((item) => item.textContent)
    expect(entities).toEqual(['ES_DNI: 1', 'PERSON: 2'])
    expect(screen.getByText(ANONYMIZED)).toBeDefined()

    const anonymized = container.querySelector('.result__anonymized')
    expect(anonymized?.tagName).toBe('PRE')

    fireEvent.click(
      screen.getByRole('button', { name: 'Continuar a la conversación' }),
    )
    expect(screen.queryByRole('button', { name: 'Probar con otro documento' })).toBeNull()
    expect(container.querySelector('main, header, nav, footer')).toBeNull()
  })

  it('muestra un aviso si no hay entidades o confianza', () => {
    renderPage({
      ...VALID,
      confidence: null,
      entities_count: {},
    })

    expect(screen.getByText('Confianza no disponible.')).toBeDefined()
    expect(
      screen.getByText('No se han detectado entidades que anonimizar.'),
    ).toBeDefined()
    expect(
      screen.getByRole('button', { name: 'Continuar a la conversación' }),
    ).toBeDefined()
  })

  it('no ofrece continuar si el texto anonimizado es nulo', () => {
    renderPage({ ...VALID, anonymized_text: null })

    expect(
      screen.queryByRole('button', { name: 'Continuar a la conversación' }),
    ).toBeNull()
  })

  it('muestra el aviso de retenido sin texto, entidades ni confianza', () => {
    const { onRestart } = renderPage(RETAINED)

    expect(screen.getByRole('heading', { name: 'Documento retenido' })).toBeDefined()
    expect(
      screen.getByText(
        'No se ha podido procesar el documento con garantías. Puedes intentarlo con otra copia.',
      ),
    ).toBeDefined()
    expect(screen.queryByText(/Confianza/)).toBeNull()
    expect(screen.queryByRole('listitem')).toBeNull()
    expect(screen.queryByText(ANONYMIZED)).toBeNull()
    expect(screen.queryByText('baja_confianza')).toBeNull()
    expect(
      screen.queryByRole('button', { name: 'Continuar a la conversación' }),
    ).toBeNull()

    fireEvent.click(screen.getByRole('button', { name: 'Probar con otro documento' }))
    expect(onRestart).toHaveBeenCalledTimes(1)
  })

  it('muestra el aviso de ilegible sin texto, entidades ni confianza', () => {
    const { onRestart } = renderPage(ILLEGIBLE)

    expect(screen.getByRole('heading', { name: 'Documento ilegible' })).toBeDefined()
    expect(
      screen.getByText(
        'El documento no contiene texto que se pueda leer. Puedes intentarlo con otro fichero.',
      ),
    ).toBeDefined()
    expect(screen.queryByText(/Confianza/)).toBeNull()
    expect(screen.queryByRole('listitem')).toBeNull()
    expect(screen.queryByText('texto_vacio')).toBeNull()
    expect(
      screen.queryByRole('button', { name: 'Continuar a la conversación' }),
    ).toBeNull()

    fireEvent.click(screen.getByRole('button', { name: 'Probar con otro documento' }))
    expect(onRestart).toHaveBeenCalledTimes(1)
  })

  it('no muestra el texto original en ninguno de los tres estados', () => {
    const { unmount } = renderPage(VALID)
    expect(screen.queryByText(ORIGINAL)).toBeNull()
    unmount()

    renderPage(RETAINED)
    expect(screen.queryByText(ORIGINAL)).toBeNull()
    cleanup()

    renderPage(ILLEGIBLE)
    expect(screen.queryByText(ORIGINAL)).toBeNull()
  })
})
