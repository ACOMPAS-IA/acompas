// Contrato de POST /api/anonymization (ficha ACO-024, sección 8).
// ACO-019 autentica la llamada a través del cliente centralizado.

import { ApiError, SessionExpiredError, apiRequest } from './client.ts'

// Códigos documentados del endpoint de anonimización (ACO-024, sección 8.4).
// `forbidden` y `auth_unavailable` los admite siempre el cliente.
const ANONYMIZATION_ALLOWED_DETAILS = [
  'invalid_request',
  'text_too_long',
  'anonymization_not_configured',
] as const

export type AnonymizationStatus = 'validado' | 'retenido' | 'ilegible'

export type AnonymizationResult = {
  status: AnonymizationStatus
  confidence: number | null
  anonymized_text: string | null
  entities_count: Record<string, number>
  reason: string | null
}

export type AnonymizeText = (
  text: string,
) => Promise<AnonymizationResult>

export class AnonymizationError extends Error {
  // Código del backend («text_too_long», «forbidden»…) o «request_failed».
  readonly detail: string

  constructor(detail: string) {
    super(`Anonymization request failed: ${detail}`)
    this.name = 'AnonymizationError'
    this.detail = detail
  }
}

export async function anonymizeText(
  text: string,
): Promise<AnonymizationResult> {
  try {
    return await apiRequest<AnonymizationResult>(
      '/api/anonymization',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      },
      { allowedDetails: ANONYMIZATION_ALLOWED_DETAILS },
    )
  } catch (error) {
    // SessionExpiredError es subclase de ApiError: se comprueba antes para no
    // ocultar la caducidad de la sesión.
    if (error instanceof SessionExpiredError) throw error
    if (error instanceof ApiError) throw new AnonymizationError(error.detail)
    throw error
  }
}
