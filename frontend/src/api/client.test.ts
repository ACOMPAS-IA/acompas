import { afterEach, describe, expect, it, vi, type Mock } from 'vitest'
import {
  ApiError,
  SessionExpiredError,
  createApiClient,
} from './client.ts'

function fakeResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as unknown as Response
}

function badJsonResponse(status: number): Response {
  return {
    ok: false,
    status,
    json: async () => {
      throw new SyntaxError('no es JSON')
    },
  } as unknown as Response
}

function makeClient(
  options: {
    token?: string | null
    getTokenError?: Error
    responses?: Array<Response | Error>
  } = {},
) {
  const getToken = vi.fn(async () => {
    if (options.getTokenError) throw options.getTokenError
    return options.token === undefined ? 'token-sintetico' : options.token
  })
  const notifyExpired = vi.fn()
  const responses = [...(options.responses ?? [fakeResponse({ ok: true })])]
  type FetchMock = Mock<
    (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>
  >
  const fetchMock: FetchMock = vi.fn(async () => {
    const next = responses.shift()
    if (next instanceof Error) throw next
    return next ?? fakeResponse({ ok: true })
  })
  const fetchImpl = fetchMock as unknown as typeof fetch

  return {
    api: createApiClient({ getToken, notifyExpired, fetchImpl }),
    getToken,
    notifyExpired,
    fetchMock,
  }
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('apiRequest', () => {
  it('adjunta el token, las cabeceras y las opciones de seguridad', async () => {
    const { api, getToken, fetchMock } = makeClient()

    await api.request('/api/test')

    expect(getToken).toHaveBeenCalledTimes(1)
    const init = fetchMock.mock.calls[0][1] as RequestInit
    const headers = init.headers as Headers
    expect(headers.get('Authorization')).toBe('Bearer token-sintetico')
    expect(headers.get('Accept')).toBe('application/json')
    expect(init.credentials).toBe('omit')
    expect(init.cache).toBe('no-store')
    expect(getToken.mock.invocationCallOrder[0]).toBeLessThan(
      fetchMock.mock.invocationCallOrder[0],
    )
  })

  it('no permite que el llamador sobrescriba Authorization', async () => {
    const { api, fetchMock } = makeClient()

    await api.request('/api/test', {
      headers: { Authorization: 'Bearer token-falso' },
    })

    const init = fetchMock.mock.calls[0][1] as RequestInit
    expect((init.headers as Headers).get('Authorization')).toBe(
      'Bearer token-sintetico',
    )
  })

  it('sin token no llama a fetch y emite la expiración', async () => {
    const { api, fetchMock, notifyExpired } = makeClient({ token: null })

    await expect(api.request('/api/test')).rejects.toBeInstanceOf(
      SessionExpiredError,
    )
    expect(fetchMock).not.toHaveBeenCalled()
    expect(notifyExpired).toHaveBeenCalledTimes(1)
  })

  it('trata un fallo de getAccessToken como sesión caducada', async () => {
    const { api, fetchMock, notifyExpired } = makeClient({
      getTokenError: new Error('sin sesión'),
    })

    await expect(api.request('/api/test')).rejects.toBeInstanceOf(
      SessionExpiredError,
    )
    expect(fetchMock).not.toHaveBeenCalled()
    expect(notifyExpired).toHaveBeenCalledTimes(1)
  })

  it('un 401 emite la expiración y lanza SessionExpiredError', async () => {
    const { api, notifyExpired } = makeClient({
      responses: [fakeResponse({ detail: 'unauthorized' }, 401)],
    })

    await expect(api.request('/api/test')).rejects.toBeInstanceOf(
      SessionExpiredError,
    )
    expect(notifyExpired).toHaveBeenCalledTimes(1)
  })

  it('un 403 no cierra la sesión', async () => {
    const { api, notifyExpired } = makeClient({
      responses: [fakeResponse({ detail: 'forbidden' }, 403)],
    })

    await expect(api.request('/api/test')).rejects.toMatchObject({
      status: 403,
      detail: 'forbidden',
    })
    expect(notifyExpired).not.toHaveBeenCalled()
  })

  it('conserva un código permitido por la petición', async () => {
    const { api } = makeClient({
      responses: [fakeResponse({ detail: 'llm_busy' }, 503)],
    })

    await expect(
      api.request('/api/conversation', {}, { allowedDetails: ['llm_busy'] }),
    ).rejects.toMatchObject({ status: 503, detail: 'llm_busy' })
  })

  it('convierte un código no permitido en request_failed', async () => {
    const { api } = makeClient({
      responses: [fakeResponse({ detail: 'traza_interna' }, 500)],
    })

    await expect(api.request('/api/test')).rejects.toMatchObject({
      status: 500,
      detail: 'request_failed',
    })
  })

  it('convierte un cuerpo no JSON en request_failed', async () => {
    const { api } = makeClient({
      responses: [badJsonResponse(422)],
    })

    await expect(api.request('/api/test')).rejects.toMatchObject({
      status: 422,
      detail: 'request_failed',
    })
  })

  it('convierte un error de red en status 0', async () => {
    const { api } = makeClient({
      responses: [new Error('sin red')],
    })

    await expect(api.request('/api/test')).rejects.toMatchObject({
      status: 0,
      detail: 'request_failed',
    })
  })

  it('convierte un JSON inválido de una respuesta 2xx en request_failed', async () => {
    const { api } = makeClient({
      responses: [badJsonResponse(200)],
    })

    await expect(api.request('/api/test')).rejects.toMatchObject({
      status: 200,
      detail: 'request_failed',
    })
  })

  it('no expone el token en el error ni en la consola', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
    const consoleLog = vi.spyOn(console, 'log').mockImplementation(() => {})
    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const { api } = makeClient({
      token: 'token-secreto-sintetico',
      responses: [fakeResponse({ detail: 'traza_interna' }, 500)],
    })

    const error: unknown = await api.request('/api/test').catch((reason) => reason)

    expect(error).toBeInstanceOf(ApiError)
    const apiError = error as ApiError
    expect(apiError.message).not.toContain('token-secreto-sintetico')
    expect(apiError.message).not.toContain('traza_interna')
    expect(consoleError).not.toHaveBeenCalled()
    expect(consoleLog).not.toHaveBeenCalled()
    expect(consoleWarn).not.toHaveBeenCalled()
  })

  it('usa el cliente por defecto sin dependencias inyectadas', () => {
    expect(createApiClient()).toHaveProperty('request')
  })
})
