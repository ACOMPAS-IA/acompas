import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
} from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type {
  ConversationRequest,
  ConversationResponse,
  SendConversation,
} from '../api/conversation.ts'
import { ConversationPage } from './ConversationPage.tsx'

// Textos breves e inventados, con etiquetas de anonimización (ficha ACO-030, sección 9).
const DOCUMENTS = [{ text: 'Informe inventado de [PACIENTE]. Firma [SANITARIO_1].' }]
const ANSWER = 'Respuesta inventada sobre el informe.'
const ERROR_TEXT = 'No se ha podido obtener respuesta. Inténtalo de nuevo.'
const TRUNCATED_TEXT = 'La respuesta se ha cortado por su longitud.'
const LIMIT_TEXT = 'Has llegado al máximo de 10 preguntas en esta conversación.'

afterEach(cleanup)

function answering(answer = ANSWER, truncated = false) {
  return vi.fn<SendConversation>(async () => ({ answer, truncated }))
}

function deferred() {
  let resolve!: (value: ConversationResponse) => void
  let reject!: (reason: unknown) => void
  const promise = new Promise<ConversationResponse>((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

function field() {
  return screen.getByRole('textbox', { name: 'Tu pregunta' })
}

function sendButton() {
  return screen.getByRole('button', { name: 'Enviar' })
}

function type(text: string) {
  fireEvent.change(field(), { target: { value: text } })
}

async function ask(text: string) {
  type(text)
  await act(async () => {
    fireEvent.click(sendButton())
  })
}

describe('ConversationPage', () => {
  it('muestra la pregunta y la respuesta', async () => {
    const send = answering()
    render(<ConversationPage documents={DOCUMENTS} send={send} />)

    await ask('¿Qué significa en rango?')

    expect(screen.getByText('¿Qué significa en rango?')).toBeDefined()
    expect(screen.getByText(ANSWER)).toBeDefined()
    expect(send).toHaveBeenCalledWith({
      documents: DOCUMENTS,
      messages: [{ role: 'user', content: '¿Qué significa en rango?' }],
    })
    expect((field() as HTMLTextAreaElement).value).toBe('')
  })

  it('envía la conversación completa con los documentos en la segunda pregunta', async () => {
    const send = answering()
    render(<ConversationPage documents={DOCUMENTS} send={send} />)

    await ask('Primera pregunta')
    await ask('Segunda pregunta')

    expect(send).toHaveBeenCalledTimes(2)
    const request: ConversationRequest = send.mock.calls[1][0]
    expect(request).toEqual({
      documents: DOCUMENTS,
      messages: [
        { role: 'user', content: 'Primera pregunta' },
        { role: 'assistant', content: ANSWER },
        { role: 'user', content: 'Segunda pregunta' },
      ],
    })
  })

  it('desactiva el envío con la pregunta vacía y mientras espera', async () => {
    const pending = deferred()
    const send = vi.fn<SendConversation>(() => pending.promise)
    render(<ConversationPage documents={DOCUMENTS} send={send} />)

    expect((sendButton() as HTMLButtonElement).disabled).toBe(true)
    type('   ')
    expect((sendButton() as HTMLButtonElement).disabled).toBe(true)

    type('Pregunta')
    expect((sendButton() as HTMLButtonElement).disabled).toBe(false)
    fireEvent.click(sendButton())

    expect(screen.getByRole('status').textContent).toBe('Esperando respuesta…')
    expect((sendButton() as HTMLButtonElement).disabled).toBe(true)
    type('Otra pregunta')
    fireEvent.keyDown(field(), { key: 'Enter' })
    expect(send).toHaveBeenCalledTimes(1)

    await act(async () => {
      pending.resolve({ answer: ANSWER, truncated: false })
    })
    expect(screen.queryByText('Esperando respuesta…')).toBeNull()
    expect(screen.getByText(ANSWER)).toBeDefined()
  })

  it('muestra el aviso de truncado', async () => {
    render(<ConversationPage documents={DOCUMENTS} send={answering(ANSWER, true)} />)

    await ask('Pregunta larga')

    expect(screen.getByText(TRUNCATED_TEXT)).toBeDefined()
  })

  it('no muestra el aviso si la respuesta no se ha cortado', async () => {
    render(<ConversationPage documents={DOCUMENTS} send={answering()} />)

    await ask('Pregunta')

    expect(screen.queryByText(TRUNCATED_TEXT)).toBeNull()
  })

  it('muestra el error, conserva la pregunta y permite reenviarla', async () => {
    const send = vi
      .fn<SendConversation>()
      .mockRejectedValueOnce(new Error('llm_busy'))
      .mockResolvedValueOnce({ answer: ANSWER, truncated: false })
    render(<ConversationPage documents={DOCUMENTS} send={send} />)

    await ask('Pregunta que falla')

    expect(screen.getByRole('alert').textContent).toBe(ERROR_TEXT)
    expect((field() as HTMLTextAreaElement).value).toBe('Pregunta que falla')
    expect(screen.queryByText('Pregunta que falla', { selector: 'p' })).toBeNull()

    await act(async () => {
      fireEvent.click(sendButton())
    })

    expect(screen.queryByRole('alert')).toBeNull()
    expect(screen.getByText(ANSWER)).toBeDefined()
    expect(send.mock.calls[1][0].messages).toEqual([
      { role: 'user', content: 'Pregunta que falla' },
    ])
  })

  it('muestra como texto una respuesta con etiquetas HTML', async () => {
    const html = '<b>negrita</b> <img src="x" onerror="alert(1)"> <script>alert(1)</script>'
    const { container } = render(
      <ConversationPage documents={DOCUMENTS} send={answering(html)} />,
    )

    await ask('Pregunta')

    expect(screen.getByText(html)).toBeDefined()
    expect(container.querySelector('b, img, script')).toBeNull()
  })

  it('da nombre accesible al campo y al botón', () => {
    render(<ConversationPage documents={DOCUMENTS} send={answering()} />)

    expect(field()).toBeDefined()
    expect(sendButton()).toBeDefined()
    expect(field().getAttribute('enterkeyhint')).toBe('send')
  })

  it('envía con Enter y no con Mayús+Enter', async () => {
    const send = answering()
    render(<ConversationPage documents={DOCUMENTS} send={send} />)

    type('Pregunta por teclado')
    fireEvent.keyDown(field(), { key: 'Enter', shiftKey: true })
    expect(send).not.toHaveBeenCalled()

    await act(async () => {
      fireEvent.keyDown(field(), { key: 'Enter' })
    })

    expect(send).toHaveBeenCalledTimes(1)
    expect(screen.getByText(ANSWER)).toBeDefined()
  })

  it('no usa <main> como elemento raíz', () => {
    const { container } = render(
      <ConversationPage documents={DOCUMENTS} send={answering()} />,
    )

    expect(container.firstElementChild?.tagName).toBe('SECTION')
    expect(screen.queryByRole('main')).toBeNull()
  })

  it('pone el texto largo en una burbuja que lo parte', async () => {
    const longWord = 'a'.repeat(500)
    render(<ConversationPage documents={DOCUMENTS} send={answering(longWord)} />)

    await ask('Pregunta')

    const bubble = screen.getByText(longWord).closest('li')
    expect(bubble?.classList.contains('conversation__bubble')).toBe(true)
    expect(bubble?.classList.contains('conversation__bubble--assistant')).toBe(true)
  })

  it('se detiene al llegar a 10 preguntas', async () => {
    const send = answering()
    render(<ConversationPage documents={DOCUMENTS} send={send} />)

    for (let index = 1; index <= 9; index++) {
      await ask(`Pregunta ${index}`)
    }
    expect(screen.queryByText(LIMIT_TEXT)).toBeNull()
    expect((field() as HTMLTextAreaElement).disabled).toBe(false)

    await ask('Pregunta 10')

    expect(send).toHaveBeenCalledTimes(10)
    expect(send.mock.calls[9][0].messages).toHaveLength(19)
    expect(screen.getByText(LIMIT_TEXT)).toBeDefined()
    expect((field() as HTMLTextAreaElement).disabled).toBe(true)
    expect((sendButton() as HTMLButtonElement).disabled).toBe(true)

    fireEvent.keyDown(field(), { key: 'Enter' })
    expect(send).toHaveBeenCalledTimes(10)
  })
})
