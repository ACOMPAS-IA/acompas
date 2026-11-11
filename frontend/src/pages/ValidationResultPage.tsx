import { useId } from 'react'
import type { AnonymizationResult } from '../api/anonymization.ts'
import './ValidationResultPage.css'

type ValidationResultPageProps = {
  result: AnonymizationResult
  onContinue: () => void
  onRestart: () => void
}

// ACO-030, sección 8: el contrato de conversación limita cada documento a
// 30 000 caracteres (MAX_DOCUMENT_CHARS del backend).
export const MAX_CONVERSATION_DOCUMENT_CHARS = 30_000

const RETAINED_TEXT =
  'No se ha podido procesar el documento con garantías. Puedes intentarlo con otra copia.'

const ILLEGIBLE_TEXT =
  'El documento no contiene texto que se pueda leer. Puedes intentarlo con otro fichero.'

const TOO_LONG_TEXT =
  'El documento es demasiado largo una vez anonimizado y no se puede usar en la conversación. Prueba con un documento más corto.'

// Se cuenta por puntos de código, como UploadPage y el len() de Python del
// backend; .length cuenta unidades UTF-16 y rechazaría texto admitido.
// eslint-disable-next-line react-refresh/only-export-components -- Predicado compartido y probado para impedir navegar con un documento no admitido por ACO-030.
export function canOpenConversation(
  result: AnonymizationResult | null,
): boolean {
  if (result === null || result.status !== 'validado') return false
  const { anonymized_text: text } = result
  return (
    text !== null &&
    Array.from(text).length <= MAX_CONVERSATION_DOCUMENT_CHARS
  )
}

function formatConfidence(confidence: number): string {
  const percentage = (confidence * 100).toFixed(1).replace('.', ',')
  return `Confianza del documento: ${percentage} %`
}

// Se monta dentro de AppShell (ACO-017), que ya pinta <main>, la cabecera,
// la navegación y el pie del disclaimer.
export function ValidationResultPage({
  result,
  onContinue,
  onRestart,
}: ValidationResultPageProps) {
  const titleId = useId()
  const validated =
    result.status === 'validado' && result.anonymized_text !== null
  const canContinue = canOpenConversation(result)

  return (
    <section className="result" aria-labelledby={titleId}>
      <h2 id={titleId} className="result__title">
        Resultado de la validación
      </h2>

      {validated && (
        <>
          <h3 className="result__subtitle">Documento validado</h3>
          <p className="result__text">
            El documento se ha anonimizado correctamente y puedes consultarlo.
          </p>

          <p className="result__confidence">
            {result.confidence === null
              ? 'Confianza no disponible.'
              : formatConfidence(result.confidence)}
          </p>

          <h3 className="result__subtitle">Entidades detectadas</h3>
          {Object.keys(result.entities_count).length === 0 ? (
            <p className="result__text">
              No se han detectado entidades que anonimizar.
            </p>
          ) : (
            <ul className="result__entities">
              {Object.entries(result.entities_count)
                .sort(([left], [right]) => left.localeCompare(right))
                .map(([type, count]) => (
                  <li key={type} className="result__entity">
                    {`${type}: ${count}`}
                  </li>
                ))}
            </ul>
          )}

          <h3 className="result__subtitle">Texto anonimizado</h3>
          <pre className="result__anonymized">{result.anonymized_text}</pre>

          {canContinue ? (
            <button
              type="button"
              className="result__button"
              onClick={onContinue}
            >
              Continuar a la conversación
            </button>
          ) : (
            <p className="result__text">{TOO_LONG_TEXT}</p>
          )}
        </>
      )}

      {result.status === 'retenido' && (
        <>
          <h3 className="result__subtitle">Documento retenido</h3>
          <p className="result__text">{RETAINED_TEXT}</p>
          <button type="button" className="result__button" onClick={onRestart}>
            Probar con otro documento
          </button>
        </>
      )}

      {result.status === 'ilegible' && (
        <>
          <h3 className="result__subtitle">Documento ilegible</h3>
          <p className="result__text">{ILLEGIBLE_TEXT}</p>
          <button type="button" className="result__button" onClick={onRestart}>
            Probar con otro documento
          </button>
        </>
      )}
    </section>
  )
}
