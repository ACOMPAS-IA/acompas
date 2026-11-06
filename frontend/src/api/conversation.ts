// Contrato de POST /api/conversation (ficha ACO-030, sección 8).
// ACO-019 autentica el envío a través del cliente centralizado.

import { ApiError, SessionExpiredError, apiRequest } from './client.ts'

// Códigos documentados del endpoint de conversación (ACO-030, sección 8.3).
const CONVERSATION_ALLOWED_DETAILS = [
  'llm_not_configured',
  'llm_busy',
  'llm_unavailable',
  'llm_timeout',
  'llm_error',
] as const

export type ConversationDocument = {
  text: string
}

export type ConversationRole = 'user' | 'assistant'

export type ConversationMessage = {
  role: ConversationRole
  content: string
}

export type ConversationRequest = {
  documents: ConversationDocument[]
  messages: ConversationMessage[]
}

export type ConversationResponse = {
  answer: string
  truncated: boolean
}

export type SendConversation = (
  request: ConversationRequest,
) => Promise<ConversationResponse>

export class ConversationError extends Error {
  // Código del backend («llm_busy», «llm_error»…) o «request_failed».
  readonly detail: string

  constructor(detail: string) {
    super(`Conversation request failed: ${detail}`)
    this.name = 'ConversationError'
    this.detail = detail
  }
}

export async function sendConversation(
  request: ConversationRequest,
): Promise<ConversationResponse> {
  try {
    return await apiRequest<ConversationResponse>(
      '/api/conversation',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      },
      { allowedDetails: CONVERSATION_ALLOWED_DETAILS },
    )
  } catch (error) {
    // La sesión caducada no se oculta: la gestiona useAuthSession.
    if (error instanceof SessionExpiredError) throw error
    if (error instanceof ApiError) throw new ConversationError(error.detail)
    throw error
  }
}
