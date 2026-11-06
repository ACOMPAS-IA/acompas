import { authService } from '../auth/authService.ts'
import { notifySessionExpired } from '../auth/sessionExpiry.ts'

// Códigos de autenticación de ACO-014. Siempre se admiten.
const AUTH_ALLOWED_DETAILS = [
  'unauthorized',
  'forbidden',
  'auth_unavailable',
] as const

const AUTH_DETAILS = new Set<string>(AUTH_ALLOWED_DETAILS)

export class ApiError extends Error {
  readonly status: number
  // Código contractual de la API o «request_failed». Nunca el cuerpo original.
  readonly detail: string

  constructor(status: number, detail: string) {
    super(`API request failed: ${detail}`)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

export class SessionExpiredError extends ApiError {
  constructor() {
    super(401, 'unauthorized')
    this.name = 'SessionExpiredError'
  }
}

export type ApiRequestOptions = {
  // Códigos `detail` que este endpoint puede devolver. Cualquier otro se
  // convierte en «request_failed» para no propagar detalles internos.
  allowedDetails?: readonly string[]
}

export type ApiClientDependencies = {
  getToken?: () => Promise<string | null>
  notifyExpired?: () => void
  fetchImpl?: typeof fetch
}

async function readDetail(response: Response): Promise<string | null> {
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
    // Cuerpo vacío, no JSON o respuesta sin cuerpo.
  }
  return null
}

export function createApiClient(deps: ApiClientDependencies = {}) {
  const getToken = deps.getToken ?? (() => authService.getAccessToken())
  const notifyExpired = deps.notifyExpired ?? notifySessionExpired
  const fetchImpl = deps.fetchImpl ?? fetch

  async function request<T>(
    path: string,
    init: RequestInit = {},
    options: ApiRequestOptions = {},
  ): Promise<T> {
    const token = await getToken().catch(() => null)

    if (!token) {
      notifyExpired()
      throw new SessionExpiredError()
    }

    const headers = new Headers(init.headers)
    headers.set('Accept', 'application/json')
    // El token de ACO-018 prevalece: el llamador no puede sobrescribirlo.
    headers.set('Authorization', `Bearer ${token}`)

    let response: Response
    try {
      response = await fetchImpl(path, {
        ...init,
        headers,
        credentials: 'omit',
        cache: 'no-store',
      })
    } catch {
      throw new ApiError(0, 'request_failed')
    }

    if (response.status === 401) {
      notifyExpired()
      throw new SessionExpiredError()
    }

    if (response.status === 403) {
      throw new ApiError(403, 'forbidden')
    }

    if (!response.ok) {
      const detail = await readDetail(response)
      const allowed = new Set<string>([
        ...AUTH_DETAILS,
        ...(options.allowedDetails ?? []),
      ])
      throw new ApiError(
        response.status,
        detail && allowed.has(detail) ? detail : 'request_failed',
      )
    }

    try {
      return (await response.json()) as T
    } catch {
      throw new ApiError(response.status, 'request_failed')
    }
  }

  return { request }
}

export const apiRequest = createApiClient().request
