// Contrato de POST /api/conversation (ficha ACO-030, sección 8).
// ACO-019 puede pasar a ConversationPage su propia función de envío, autenticada.

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

async function readDetail(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json()
    if (
      typeof body === 'object' &&
      body !== null &&
      'detail' in body &&
      typeof body.detail === 'string'
    ) {
      return body.detail
    }
  } catch {
    // Cuerpo vacío o no JSON.
  }
  // Un 422 trae una lista de errores, no un código.
  return 'request_failed'
}

export async function sendConversation(
  request: ConversationRequest,
): Promise<ConversationResponse> {
  const response = await fetch('/api/conversation', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
  if (!response.ok) {
    throw new ConversationError(await readDetail(response))
  }
  return (await response.json()) as ConversationResponse
}
