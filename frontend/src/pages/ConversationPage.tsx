import { useId, useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'
import {
  sendConversation,
  type ConversationDocument,
  type ConversationRole,
  type SendConversation,
} from '../api/conversation.ts'
import './ConversationPage.css'

// El backend admite hasta 21 mensajes (MAX_MESSAGES), es decir, 11 preguntas
// con sus 10 respuestas. La página se queda en 10 preguntas, por debajo de ese
// límite, para que la conversación nunca reciba un 422 por su longitud.
const MAX_QUESTIONS = 10

const MAX_QUESTION_CHARS = 2000

type Entry = {
  role: ConversationRole
  content: string
  truncated?: boolean
}

type ConversationPageProps = {
  documents: ConversationDocument[]
  send?: SendConversation
}

const SPEAKERS: Record<ConversationRole, string> = {
  user: 'Tú',
  assistant: 'ACOMPAS',
}

function Bubble({ entry }: { entry: Entry }) {
  return (
    <li
      className={`conversation__bubble conversation__bubble--${entry.role}`}
    >
      <span className="conversation__speaker">{SPEAKERS[entry.role]}</span>
      <p className="conversation__text">{entry.content}</p>
      {entry.truncated && (
        <p className="conversation__notice">
          La respuesta se ha cortado por su longitud.
        </p>
      )}
    </li>
  )
}

// Se monta dentro de AppShell (ACO-017), que ya pinta <main>, la cabecera,
// la navegación y el pie del disclaimer.
export function ConversationPage({
  documents,
  send = sendConversation,
}: ConversationPageProps) {
  const questionId = useId()
  // Solo en memoria: la conversación no se guarda en el navegador.
  const [entries, setEntries] = useState<Entry[]>([])
  const [question, setQuestion] = useState('')
  const [pending, setPending] = useState<string | null>(null)
  const [failed, setFailed] = useState(false)

  const answered = entries.filter((entry) => entry.role === 'user').length
  const limitReached = answered >= MAX_QUESTIONS
  const waiting = pending !== null
  const canSend = !waiting && !limitReached && question.trim() !== ''

  async function submit() {
    if (!canSend) {
      return
    }
    const text = question
    const history = entries.map(({ role, content }) => ({ role, content }))
    setPending(text)
    setQuestion('')
    setFailed(false)
    try {
      // Conversación completa en cada pregunta (ficha ACO-030, P1).
      const response = await send({
        documents,
        messages: [...history, { role: 'user', content: text }],
      })
      setEntries((previous) => [
        ...previous,
        { role: 'user', content: text },
        {
          role: 'assistant',
          content: response.answer,
          truncated: response.truncated,
        },
      ])
    } catch {
      // Se conserva la pregunta para reenviarla.
      setQuestion(text)
      setFailed(true)
    } finally {
      setPending(null)
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void submit()
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    // Enter envía y Mayús+Enter añade un salto de línea. Se respeta la
    // composición de los métodos de entrada.
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault()
      void submit()
    }
  }

  return (
    <section className="conversation" aria-labelledby={`${questionId}-title`}>
      <h2 id={`${questionId}-title`} className="conversation__title">
        Conversación
      </h2>

      {(entries.length > 0 || waiting) && (
        <ol className="conversation__messages">
          {entries.map((entry, index) => (
            <Bubble key={index} entry={entry} />
          ))}
          {waiting && <Bubble entry={{ role: 'user', content: pending }} />}
        </ol>
      )}

      {waiting && (
        <p className="conversation__status" role="status">
          Esperando respuesta…
        </p>
      )}
      {failed && (
        <p className="conversation__error" role="alert">
          No se ha podido obtener respuesta. Inténtalo de nuevo.
        </p>
      )}
      {limitReached && (
        <p className="conversation__status" role="status">
          {`Has llegado al máximo de ${MAX_QUESTIONS} preguntas en esta conversación.`}
        </p>
      )}

      <form className="conversation__form" onSubmit={handleSubmit}>
        <label className="conversation__label" htmlFor={questionId}>
          Tu pregunta
        </label>
        <div className="conversation__row">
          <textarea
            id={questionId}
            className="conversation__input"
            rows={3}
            maxLength={MAX_QUESTION_CHARS}
            enterKeyHint="send"
            value={question}
            readOnly={waiting}
            disabled={limitReached}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            type="submit"
            className="conversation__send"
            disabled={!canSend}
          >
            Enviar
          </button>
        </div>
      </form>
    </section>
  )
}
