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

const REPLACED_LEAD = 'Hemos sustituido los datos que te identifican:'
const NOTHING_REPLACED = 'No se han detectado datos que te identifiquen.'
const OTHER_DATA = 'otros datos identificativos'

// Las etiquetas de las entidades son códigos internos (`ES_DNI`, `DATE_TIME`).
// El paciente ve el texto anonimizado con `[DNI]` o `[FECHA_NACIMIENTO]`, así
// que aquí se traducen a lenguaje natural y se ordenan por importancia: primero
// sus datos, después las otras personas y al final los lugares.
const REPLACED_LABELS: ReadonlyArray<readonly [readonly string[], string]> = [
  [['PACIENTE'], 'tu nombre'],
  [['ES_DNI'], 'tu DNI'],
  [['ES_NIE'], 'tu NIE'],
  [['ES_HISTORIA_CLINICA'], 'tu número de historia clínica'],
  [['ID_ASEGURAMIENTO'], 'tu número de aseguramiento'],
  [['ID_CONTACTO_ASISTENCIAL'], 'tu número de contacto asistencial'],
  [['DATE_TIME'], 'tu fecha de nacimiento'],
  [['PHONE_NUMBER'], 'teléfonos'],
  [['EMAIL_ADDRESS'], 'correos electrónicos'],
  [['CALLE'], 'direcciones'],
  [['PERSONAL_SANITARIO'], 'nombres del personal sanitario'],
  [['FAMILIAR'], 'nombres de familiares'],
  [['PERSON'], 'nombres de personas'],
  [['HOSPITAL'], 'el hospital'],
  [['CENTRO_SALUD'], 'el centro de salud'],
  [['INSTITUCION'], 'instituciones'],
  [['TERRITORIO'], 'localidades'],
  [['ID_EMPLEO_PERSONAL_SANITARIO'], 'identificadores del personal sanitario'],
  [['ID_TITULACION_PERSONAL_SANITARIO'], 'titulaciones del personal sanitario'],
]

// Traduce el recuento por tipo a la lista que ve el paciente. Un tipo que no
// esté en la tabla no se adivina: se agrupa como «otros datos identificativos».
// eslint-disable-next-line react-refresh/only-export-components -- Predicado compartido y probado para impedir que se muestren códigos internos.
export function replacedDataLabels(
  entitiesCount: Record<string, number>,
): string[] {
  const known = new Set(REPLACED_LABELS.flatMap(([types]) => types))
  const labels = REPLACED_LABELS.filter(([types]) =>
    types.some((type) => (entitiesCount[type] ?? 0) > 0),
  ).map(([, label]) => label)

  const hasUnknown = Object.entries(entitiesCount).some(
    ([type, count]) => count > 0 && !known.has(type),
  )
  if (hasUnknown) labels.push(OTHER_DATA)

  return labels
}

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
  const replaced = replacedDataLabels(result.entities_count)

  return (
    <section className="result" aria-labelledby={titleId}>
      <h2 id={titleId} className="result__title">
        Resultado de la validación
      </h2>

      {validated && (
        <>
          <h3 className="result__subtitle">Documento validado</h3>

          <p className="result__text">
            {replaced.length === 0 ? NOTHING_REPLACED : REPLACED_LEAD}
          </p>

          {replaced.length > 0 && (
            <ul className="result__replaced">
              {replaced.map((label) => (
                <li key={label} className="result__replaced-item">
                  {label}
                </li>
              ))}
            </ul>
          )}

          <p className="result__notice">
            Los corchetes son una ayuda para leer el texto. Pueden no acertar
            con el papel de la persona: [PERSONA_1] puede ser un médico o un
            familiar. Lo importante es que el dato que te identifica ya no
            está, aunque la etiqueta no acierte con el rol.
          </p>

          <p className="result__notice">
            También puede pasar lo contrario: que hayamos sustituido un dato
            que te ayudaba a entender el informe, como una fecha. Es
            deliberado. Ante la duda, preferimos quitar el dato a dejar
            escapar algo que te identifique.
          </p>

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
