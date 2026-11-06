import { afterEach, describe, expect, it, vi } from 'vitest'

const { apiRequestMock } = vi.hoisted(() => ({
  apiRequestMock: vi.fn(),
}))

vi.mock('./client.ts', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./client.ts')>()
  return {
    ...actual,
    apiRequest: apiRequestMock,
  }
})

import { ApiError, SessionExpiredError } from './client.ts'
import {
  ConversationError,
  sendConversation,
  type ConversationRequest,
  type ConversationResponse,
} from './conversation.ts'

const REQUEST: ConversationRequest = {
  documents: [{ text: 'Informe inventado de [PACIENTE].' }],
  messages: [{ role: 'user', content: '¿Qué significa el CA 19-9?' }],
}

const RESPONSE: ConversationResponse = {
  answer: 'Respuesta inventada.',
  truncated: false,
}

afterEach(() => {
  apiRequestMock.mockReset()
})

describe('sendConversation', () => {
  it('usa el cliente centralizado y el contrato de ACO-030', async () => {
    apiRequestMock.mockResolvedValue(RESPONSE)

    await expect(sendConversation(REQUEST)).resolves.toEqual(RESPONSE)

    expect(apiRequestMock).toHaveBeenCalledWith(
      '/api/conversation',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(REQUEST),
      },
      {
        allowedDetails: [
          'llm_not_configured',
          'llm_busy',
          'llm_unavailable',
          'llm_timeout',
          'llm_error',
        ],
      },
    )
  })

  it('convierte un ApiError permitido en ConversationError', async () => {
    apiRequestMock.mockRejectedValue(new ApiError(503, 'llm_busy'))

    const error = await sendConversation(REQUEST).catch((reason) => reason)

    expect(error).toBeInstanceOf(ConversationError)
    expect(error.detail).toBe('llm_busy')
  })

  it('propaga SessionExpiredError sin ocultar la caducidad', async () => {
    apiRequestMock.mockRejectedValue(new SessionExpiredError())

    await expect(sendConversation(REQUEST)).rejects.toBeInstanceOf(
      SessionExpiredError,
    )
  })

  it('propaga cualquier otro error', async () => {
    const failure = new Error('fallo inesperado')
    apiRequestMock.mockRejectedValue(failure)

    await expect(sendConversation(REQUEST)).rejects.toBe(failure)
  })
})
