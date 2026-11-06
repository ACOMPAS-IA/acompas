import { useId, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import {
  AnonymizationError,
  anonymizeText,
  type AnonymizationResult,
  type AnonymizeText,
} from '../api/anonymization.ts'
import { SessionExpiredError } from '../api/client.ts'
import './UploadPage.css'

// Límites de la ficha ACO-032 (sección 8.2). 128 KiB es el peor caso UTF-8 de
// 30 000 caracteres (4 bytes por punto de código).
const MAX_FILE_BYTES = 128 * 1024
const MAX_TEXT_CHARS = 30_000

const EXTENSION_ERROR = 'Solo se admiten documentos .txt en UTF-8.'
const LIMIT_ERROR = 'El documento supera el máximo de 30 000 caracteres.'
const ENCODING_ERROR = 'El fichero no está codificado en UTF-8.'
const READ_ERROR = 'No se ha podido leer el fichero. Inténtalo de nuevo.'

const ERROR_MESSAGES: Record<string, string> = {
  invalid_request: 'No se ha podido procesar la petición. Inténtalo de nuevo.',
  text_too_long: LIMIT_ERROR,
  anonymization_not_configured:
    'El servicio de anonimización no está disponible. Avisa al equipo.',
  forbidden: 'No tienes permiso para subir documentos.',
  auth_unavailable:
    'El servicio de autenticación no está disponible. Inténtalo de nuevo.',
  request_failed: 'No se ha podido anonimizar el documento. Inténtalo de nuevo.',
}

type UploadPageProps = {
  onResult: (result: AnonymizationResult) => void
  anonymize?: AnonymizeText
}

type Phase = 'idle' | 'reading' | 'submitting'

// Se monta dentro de AppShell (ACO-017), que ya pinta <main>, la cabecera,
// la navegación y el pie del disclaimer.
export function UploadPage({
  onResult,
  anonymize = anonymizeText,
}: UploadPageProps) {
  const fileId = useId()
  const [file, setFile] = useState<File | null>(null)
  const [phase, setPhase] = useState<Phase>('idle')
  const [error, setError] = useState<string | null>(null)
  // Solo un fallo de la llamada habilita «Reintentar» con el mismo fichero.
  const [canRetry, setCanRetry] = useState(false)

  const busy = phase !== 'idle'

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null)
    setError(null)
    setCanRetry(false)
  }

  async function submit() {
    if (!file || busy) return

    setError(null)
    setCanRetry(false)

    // R-04: el nombre solo se usa para comprobar la extensión. No se copia a
    // la interfaz, a los errores ni a ningún estado visible.
    if (!file.name.toLowerCase().endsWith('.txt')) {
      setError(EXTENSION_ERROR)
      return
    }

    if (file.size > MAX_FILE_BYTES) {
      setError(LIMIT_ERROR)
      return
    }

    setPhase('reading')
    let buffer: ArrayBuffer
    try {
      buffer = await file.arrayBuffer()
    } catch {
      setPhase('idle')
      setError(READ_ERROR)
      return
    }

    let text: string
    try {
      // `fatal: true` rechaza los bytes inválidos en vez de sustituirlos por
      // U+FFFD: así se cumple el requisito de UTF-8 real.
      text = new TextDecoder('utf-8', { fatal: true }).decode(buffer)
    } catch {
      setPhase('idle')
      setError(ENCODING_ERROR)
      return
    }

    if (Array.from(text).length > MAX_TEXT_CHARS) {
      setPhase('idle')
      setError(LIMIT_ERROR)
      return
    }

    setPhase('submitting')
    try {
      const result = await anonymize(text)
      setPhase('idle')
      onResult(result)
    } catch (failure) {
      setPhase('idle')
      // La caducidad de sesión no es un error local: la gestiona
      // useAuthSession, que desmonta el flujo y vuelve al login.
      if (failure instanceof SessionExpiredError) return
      if (failure instanceof AnonymizationError) {
        setError(ERROR_MESSAGES[failure.detail] ?? ERROR_MESSAGES.request_failed)
      } else {
        setError(ERROR_MESSAGES.request_failed)
      }
      setCanRetry(true)
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void submit()
  }

  const buttonLabel = busy
    ? 'Procesando…'
    : canRetry
      ? 'Reintentar'
      : 'Subir y anonimizar'

  return (
    <section className="upload" aria-labelledby={`${fileId}-title`}>
      <h2 id={`${fileId}-title`} className="upload__title">
        Subir documento
      </h2>
      <p className="upload__intro">
        Selecciona un documento sintético en formato .txt. ACOMPAS lo
        anonimizará antes de que puedas consultarlo.
      </p>

      <form className="upload__form" onSubmit={handleSubmit}>
        <label className="upload__label" htmlFor={fileId}>
          Documento (.txt)
        </label>
        <input
          id={fileId}
          className="upload__input"
          type="file"
          accept=".txt,text/plain"
          onChange={handleFileChange}
        />
        <button
          type="submit"
          className="upload__button"
          disabled={!file || busy}
          aria-busy={busy || undefined}
        >
          {buttonLabel}
        </button>
      </form>

      {phase === 'reading' && (
        <p className="upload__status" role="status">
          Leyendo el fichero…
        </p>
      )}
      {phase === 'submitting' && (
        <p className="upload__status" role="status">
          Subiendo y anonimizando… La primera vez puede tardar mientras se carga
          el modelo.
        </p>
      )}
      {error && (
        <p className="upload__error" role="alert">
          {error}
        </p>
      )}
    </section>
  )
}
