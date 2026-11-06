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
  AnonymizationError,
  anonymizeText,
  type AnonymizationResult,
} from './anonymization.ts'

const RESULT: AnonymizationResult = {
  status: 'validado',
  confidence: 0.93,
  anonymized_text: 'Paciente: [PACIENTE]. DNI: [DNI].',
  entities_count: { PERSON: 1, ES_DNI: 1 },
  reason: null,
}

afterEach(() => {
  apiRequestMock.mockReset()
})

describe('anonymizeText', () => {
  it('usa el cliente centralizado y el contrato de ACO-024', async () => {
    apiRequestMock.mockResolvedValue(RESULT)

    await expect(anonymizeText('Texto sintético.')).resolves.toEqual(RESULT)

    expect(apiRequestMock).toHaveBeenCalledWith(
      '/api/anonymization',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: 'Texto sintético.' }),
      },
      {
        allowedDetails: [
          'invalid_request',
          'text_too_long',
          'anonymization_not_configured',
        ],
      },
    )
  })

  it('convierte un ApiError permitido en AnonymizationError', async () => {
    apiRequestMock.mockRejectedValue(new ApiError(422, 'text_too_long'))

    const error = await anonymizeText('Texto sintético.').catch(
      (reason) => reason,
    )

    expect(error).toBeInstanceOf(AnonymizationError)
    expect(error.detail).toBe('text_too_long')
  })

  it('conserva forbidden y auth_unavailable como detalles del error', async () => {
    apiRequestMock.mockRejectedValue(new ApiError(403, 'forbidden'))

    const forbidden = await anonymizeText('Texto sintético.').catch(
      (reason) => reason,
    )
    expect(forbidden).toBeInstanceOf(AnonymizationError)
    expect(forbidden.detail).toBe('forbidden')

    apiRequestMock.mockRejectedValue(new ApiError(503, 'auth_unavailable'))
    const unavailable = await anonymizeText('Texto sintético.').catch(
      (reason) => reason,
    )
    expect(unavailable).toBeInstanceOf(AnonymizationError)
    expect(unavailable.detail).toBe('auth_unavailable')
  })

  it('propaga SessionExpiredError sin ocultar la caducidad', async () => {
    apiRequestMock.mockRejectedValue(new SessionExpiredError())

    await expect(anonymizeText('Texto sintético.')).rejects.toBeInstanceOf(
      SessionExpiredError,
    )
  })

  it('propaga cualquier otro error', async () => {
    const failure = new Error('fallo inesperado')
    apiRequestMock.mockRejectedValue(failure)

    await expect(anonymizeText('Texto sintético.')).rejects.toBe(failure)
  })
})
