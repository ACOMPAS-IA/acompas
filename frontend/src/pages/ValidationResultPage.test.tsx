import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { AnonymizationResult } from '../api/anonymization.ts'
import {
  MAX_CONVERSATION_DOCUMENT_CHARS,
  ValidationResultPage,
  canOpenConversation,
  replacedDataLabels,
} from './ValidationResultPage.tsx'

// Texto inventado con etiquetas de anonimización (ACO-032, sección 9).
const ANONYMIZED = 'Paciente: [PACIENTE]. DNI: [DNI].'
const ORIGINAL = 'Paciente: Juan Pérez. DNI: 12345678Z.'

const CONTINUE_LABEL = 'Continuar a la conversación'

const REPLACED_LEAD = 'Hemos sustituido los datos que te identifican:'
const NOTHING_REPLACED = 'No se han detectado datos que te identifiquen.'

const LABEL_NOTICE = /Los corchetes son una ayuda para leer el texto/
const OVER_NOTICE = /También puede pasar lo contrario/

const TOO_LONG_TEXT =
  'El documento es demasiado largo una vez anonimizado y no se puede usar en la conversación. Prueba con un documento más corto.'

const MAX_TEXT = 'a'.repeat(MAX_CONVERSATION_DOCUMENT_CHARS)
const OVER_LIMIT_TEXT = 'a'.repeat(MAX_CONVERSATION_DOCUMENT_CHARS + 1)
const MAX_EMOJIS = '😀'.repeat(MAX_CONVERSATION_DOCUMENT_CHARS)

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

function replacedItems(): (string | null)[] {
  return screen.getAllByRole('listitem').map((item) => item.textContent)
}

describe('ValidationResultPage', () => {
  it('muestra los datos sustituidos en lenguaje natural y el texto anonimizado', () => {
    const { container, onContinue } = renderPage(VALID)

    expect(screen.getByRole('heading', { name: 'Documento validado' })).toBeDefined()
    expect(screen.getByText(REPLACED_LEAD)).toBeDefined()
    // Orden por importancia, no alfabético por el código interno.
    expect(replacedItems()).toEqual(['tu DNI', 'nombres de personas'])
    expect(screen.getByText(ANONYMIZED)).toBeDefined()

    const anonymized = container.querySelector('.result__anonymized')
    expect(anonymized?.tagName).toBe('PRE')

    fireEvent.click(screen.getByRole('button', { name: CONTINUE_LABEL }))
    expect(onContinue).toHaveBeenCalledTimes(1)
    expect(screen.queryByRole('button', { name: 'Probar con otro documento' })).toBeNull()
    expect(container.querySelector('main, header, nav, footer')).toBeNull()
  })

  it('no muestra la confianza ni los tipos internos en ningún sitio', () => {
    const { container } = renderPage(VALID)

    expect(screen.queryByText(/Confianza/)).toBeNull()
    expect(screen.queryByText(/Entidades detectadas/)).toBeNull()
    expect(screen.queryByText(/ES_DNI|DATE_TIME|PERSONAL_SANITARIO/)).toBeNull()
    // Tampoco escondidos tras un desplegable.
    expect(container.querySelector('details')).toBeNull()
  })

  it('da siempre los dos avisos sobre los límites de la anonimización', () => {
    renderPage(VALID)

    expect(screen.getByText(LABEL_NOTICE)).toBeDefined()
    expect(screen.getByText(OVER_NOTICE)).toBeDefined()
  })

  it('avisa cuando no se ha sustituido ningún dato', () => {
    renderPage({ ...VALID, entities_count: {} })

    expect(screen.getByText(NOTHING_REPLACED)).toBeDefined()
    expect(screen.queryByText(REPLACED_LEAD)).toBeNull()
    expect(screen.queryByRole('listitem')).toBeNull()
    expect(
      screen.getByRole('button', { name: CONTINUE_LABEL }),
    ).toBeDefined()
  })

  it('agrupa un tipo desconocido como otros datos identificativos', () => {
    renderPage({
      ...VALID,
      entities_count: { ES_DNI: 1, TIPO_NUEVO: 2 },
    })

    expect(replacedItems()).toEqual(['tu DNI', 'otros datos identificativos'])
  })

  it('ofrece continuar con 30 000 puntos de código', () => {
    renderPage({ ...VALID, anonymized_text: MAX_TEXT })

    expect(screen.getByRole('button', { name: CONTINUE_LABEL })).toBeDefined()
    expect(screen.queryByText(TOO_LONG_TEXT)).toBeNull()
  })

  it('avisa y no ofrece continuar con 30 001 puntos de código', () => {
    const { container } = renderPage({
      ...VALID,
      anonymized_text: OVER_LIMIT_TEXT,
    })

    expect(screen.getByText(TOO_LONG_TEXT)).toBeDefined()
    expect(screen.queryByRole('button', { name: CONTINUE_LABEL })).toBeNull()

    // El resto del resultado sigue visible (ACO-032, sección 8.4).
    expect(
      screen.getByRole('heading', { name: 'Documento validado' }),
    ).toBeDefined()
    expect(replacedItems()).toEqual(['tu DNI', 'nombres de personas'])
    expect(
      container.querySelector('.result__anonymized')?.textContent,
    ).toBe(OVER_LIMIT_TEXT)
  })

  it('cuenta puntos de código y permite 30 000 emojis', () => {
    expect(MAX_EMOJIS.length).toBe(MAX_CONVERSATION_DOCUMENT_CHARS * 2)
    renderPage({ ...VALID, anonymized_text: MAX_EMOJIS })

    expect(screen.getByRole('button', { name: CONTINUE_LABEL })).toBeDefined()
    expect(screen.queryByText(TOO_LONG_TEXT)).toBeNull()
  })

  it('no muestra el aviso de longitud en retenido ni en ilegible', () => {
    const { unmount } = renderPage(RETAINED)
    expect(screen.queryByText(TOO_LONG_TEXT)).toBeNull()
    unmount()

    renderPage(ILLEGIBLE)
    expect(screen.queryByText(TOO_LONG_TEXT)).toBeNull()
  })

  it('no ofrece continuar si el texto anonimizado es nulo', () => {
    renderPage({ ...VALID, anonymized_text: null })

    expect(
      screen.queryByRole('button', { name: CONTINUE_LABEL }),
    ).toBeNull()
  })

  it('muestra el aviso de retenido sin texto, datos sustituidos ni avisos', () => {
    const { onRestart } = renderPage(RETAINED)

    expect(screen.getByRole('heading', { name: 'Documento retenido' })).toBeDefined()
    expect(
      screen.getByText(
        'No se ha podido procesar el documento con garantías. Puedes intentarlo con otra copia.',
      ),
    ).toBeDefined()
    expect(screen.queryByText(/Confianza/)).toBeNull()
    expect(screen.queryByText(REPLACED_LEAD)).toBeNull()
    expect(screen.queryByText(LABEL_NOTICE)).toBeNull()
    expect(screen.queryByRole('listitem')).toBeNull()
    expect(screen.queryByText(ANONYMIZED)).toBeNull()
    expect(screen.queryByText('baja_confianza')).toBeNull()
    expect(
      screen.queryByRole('button', { name: CONTINUE_LABEL }),
    ).toBeNull()

    fireEvent.click(screen.getByRole('button', { name: 'Probar con otro documento' }))
    expect(onRestart).toHaveBeenCalledTimes(1)
  })

  it('muestra el aviso de ilegible sin texto, datos sustituidos ni avisos', () => {
    const { onRestart } = renderPage(ILLEGIBLE)

    expect(screen.getByRole('heading', { name: 'Documento ilegible' })).toBeDefined()
    expect(
      screen.getByText(
        'El documento no contiene texto que se pueda leer. Puedes intentarlo con otro fichero.',
      ),
    ).toBeDefined()
    expect(screen.queryByText(/Confianza/)).toBeNull()
    expect(screen.queryByText(REPLACED_LEAD)).toBeNull()
    expect(screen.queryByText(LABEL_NOTICE)).toBeNull()
    expect(screen.queryByRole('listitem')).toBeNull()
    expect(screen.queryByText('texto_vacio')).toBeNull()
    expect(
      screen.queryByRole('button', { name: CONTINUE_LABEL }),
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

describe('replacedDataLabels', () => {
  it('traduce los tipos internos a lenguaje natural en orden de importancia', () => {
    expect(
      replacedDataLabels({
        PERSONAL_SANITARIO: 3,
        HOSPITAL: 1,
        DATE_TIME: 1,
        ES_HISTORIA_CLINICA: 1,
        PACIENTE: 1,
      }),
    ).toEqual([
      'tu nombre',
      'tu número de historia clínica',
      'tu fecha de nacimiento',
      'nombres del personal sanitario',
      'el hospital',
    ])
  })

  it('no duplica etiquetas aunque haya varios tipos con el mismo texto', () => {
    expect(replacedDataLabels({ PACIENTE: 1, PERSON: 1 })).toEqual([
      'tu nombre',
      'nombres de personas',
    ])
  })

  it('ignora los tipos con recuento cero', () => {
    expect(replacedDataLabels({ ES_DNI: 0, PERSON: 0 })).toEqual([])
  })

  it('agrupa los tipos desconocidos en una sola entrada', () => {
    expect(
      replacedDataLabels({ ES_DNI: 1, TIPO_NUEVO: 2, OTRO_TIPO: 3 }),
    ).toEqual(['tu DNI', 'otros datos identificativos'])
  })

  it('devuelve una lista vacía sin datos sustituidos', () => {
    expect(replacedDataLabels({})).toEqual([])
  })
})

describe('canOpenConversation', () => {
  it('fija el límite de conversación en 30 000 caracteres', () => {
    expect(MAX_CONVERSATION_DOCUMENT_CHARS).toBe(30_000)
  })

  it('devuelve true con 30 000 puntos de código y false con 30 001', () => {
    expect(
      canOpenConversation({ ...VALID, anonymized_text: MAX_TEXT }),
    ).toBe(true)
    expect(
      canOpenConversation({ ...VALID, anonymized_text: OVER_LIMIT_TEXT }),
    ).toBe(false)
  })
})
