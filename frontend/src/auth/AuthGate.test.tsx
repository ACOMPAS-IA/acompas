import { StrictMode } from 'react'
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from '@testing-library/react'
import { User } from 'oidc-client-ts'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { AnonymizationResult } from '../api/anonymization.ts'
import { DISCLAIMER_TEXT } from '../components/disclaimer/Disclaimer.tsx'
import { buildAuthConfig } from './authConfig.ts'
import { createAuthService, type AuthManager } from './authService.ts'
import { AuthGate } from './AuthGate.tsx'
import { SESSION_EXPIRED_EVENT } from './sessionExpiry.ts'
import { CALLBACK_ERROR } from './useAuthSession.ts'

const { anonymizeTextMock, sendConversationMock } = vi.hoisted(() => ({
  anonymizeTextMock: vi.fn(),
  sendConversationMock: vi.fn(),
}))

vi.mock('../api/anonymization.ts', async (importOriginal) => {
  const actual =
    await importOriginal<typeof import('../api/anonymization.ts')>()
  return { ...actual, anonymizeText: anonymizeTextMock }
})

vi.mock('../api/conversation.ts', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/conversation.ts')>()
  return { ...actual, sendConversation: sendConversationMock }
})

const config = buildAuthConfig()

const nowInSeconds = () => Math.floor(Date.now() / 1000)

function makeUser(email = 'persona@example.test'): User {
  const now = nowInSeconds()
  return new User({
    access_token: 'token-sintetico',
    token_type: 'Bearer',
    id_token: 'id-sintetico',
    refresh_token: 'refresh-sintetico',
    expires_at: now + 300,
    profile: {
      sub: 'persona-sintetica',
      iss: 'http://localhost:8080/realms/acompas',
      aud: 'acompas-frontend',
      exp: now + 300,
      iat: now,
      email,
    },
  })
}

function createManager(overrides: Partial<AuthManager> = {}): AuthManager {
  return {
    signinRedirect: vi.fn(async () => {}),
    signinRedirectCallback: vi.fn(async () => makeUser()),
    signinSilent: vi.fn(async () => null),
    signoutRedirect: vi.fn(async () => {}),
    getUser: vi.fn(async () => null),
    removeUser: vi.fn(async () => {}),
    ...overrides,
  }
}

afterEach(() => {
  cleanup()
  window.history.replaceState(null, '', '/')
  anonymizeTextMock.mockReset()
  sendConversationMock.mockReset()
  vi.restoreAllMocks()
})

describe('AuthGate', () => {
  it('muestra el estado de comprobación mientras carga la sesión', () => {
    const service = createAuthService(
      createManager({ getUser: vi.fn(() => new Promise<User | null>(() => {})) }),
      config,
    )

    render(<AuthGate service={service} />)

    expect(screen.getByRole('status').textContent).toContain('Comprobando sesión')
  })

  it('muestra el login sin sesión, sin campos de credenciales ni pie', async () => {
    const service = createAuthService(createManager(), config)

    const { container } = render(<AuthGate service={service} />)

    expect(
      await screen.findByRole('heading', { name: 'Iniciar sesión' }),
    ).toBeDefined()
    expect(screen.getByRole('heading', { name: 'ACOMPAS' })).toBeDefined()
    expect(screen.getByRole('button', { name: 'Iniciar sesión' })).toBeDefined()
    expect(container.querySelector('input')).toBeNull()
    expect(screen.queryByRole('navigation')).toBeNull()
    expect(screen.queryByRole('contentinfo')).toBeNull()
  })

  it('inicia la redirección y bloquea el botón mientras espera', async () => {
    const signinRedirect = vi.fn(async () => {})
    const service = createAuthService(createManager({ signinRedirect }), config)

    render(<AuthGate service={service} />)

    const button = await screen.findByRole('button', { name: 'Iniciar sesión' })
    fireEvent.click(button)

    await waitFor(() => expect(signinRedirect).toHaveBeenCalledTimes(1))
    const busyButton = screen.getByRole('button', { name: 'Redirigiendo…' })
    expect(busyButton.hasAttribute('disabled')).toBe(true)
    expect(busyButton.getAttribute('aria-busy')).toBe('true')
  })

  it('muestra el AppShell autenticado con email, logout y el aviso del pie', async () => {
    const service = createAuthService(
      createManager({ getUser: vi.fn(async () => makeUser()) }),
      config,
    )

    render(<AuthGate service={service} />)

    expect(
      await screen.findByRole('navigation', { name: 'Navegación principal' }),
    ).toBeDefined()
    expect(screen.getByText('persona@example.test')).toBeDefined()
    expect(screen.getByRole('button', { name: 'Cerrar sesión' })).toBeDefined()
    expect(
      screen.getByRole('heading', { name: 'Subir documento' }),
    ).toBeDefined()
    expect(
      screen
        .getByRole('button', { name: 'Documento' })
        .getAttribute('aria-current'),
    ).toBe('page')

    const footer = screen.getByRole('contentinfo', { name: 'Aviso legal' })
    expect(within(footer).getByText(DISCLAIMER_TEXT)).toBeDefined()
  })

  it('procesa el callback una sola vez con StrictMode y limpia la URL', async () => {
    window.history.replaceState(null, '', '/auth/callback?code=abc&state=xyz')
    const signinRedirectCallback = vi.fn(async () => makeUser())
    const service = createAuthService(
      createManager({ signinRedirectCallback }),
      config,
    )

    render(
      <StrictMode>
        <AuthGate service={service} />
      </StrictMode>,
    )

    expect(
      await screen.findByRole('navigation', { name: 'Navegación principal' }),
    ).toBeDefined()
    expect(signinRedirectCallback).toHaveBeenCalledTimes(1)
    expect(window.location.pathname).toBe('/')
  })

  it('muestra un error y el login si el callback falla, sin bucle', async () => {
    window.history.replaceState(null, '', '/auth/callback?code=abc&state=xyz')
    const signinRedirectCallback = vi.fn(async () => {
      throw new Error('callback inválido')
    })
    const service = createAuthService(
      createManager({ signinRedirectCallback }),
      config,
    )

    render(
      <StrictMode>
        <AuthGate service={service} />
      </StrictMode>,
    )

    expect((await screen.findByRole('alert')).textContent).toBe(CALLBACK_ERROR)
    expect(
      screen.getByRole('button', { name: 'Iniciar sesión' }),
    ).toBeDefined()
    expect(window.location.pathname).toBe('/')
    expect(signinRedirectCallback).toHaveBeenCalledTimes(1)
  })

  it('elimina la sesión local antes de redirigir al cerrar sesión', async () => {
    const removeUser = vi.fn(async () => {})
    const signoutRedirect = vi.fn(async () => {})
    const service = createAuthService(
      createManager({
        getUser: vi.fn(async () => makeUser()),
        removeUser,
        signoutRedirect,
      }),
      config,
    )

    render(<AuthGate service={service} />)

    fireEvent.click(await screen.findByRole('button', { name: 'Cerrar sesión' }))

    expect(
      await screen.findByRole('heading', { name: 'Iniciar sesión' }),
    ).toBeDefined()
    expect(removeUser.mock.invocationCallOrder[0]).toBeLessThan(
      signoutRedirect.mock.invocationCallOrder[0],
    )
    expect(signoutRedirect).toHaveBeenCalledWith({
      id_token_hint: 'id-sintetico',
      post_logout_redirect_uri: 'http://localhost:5173/',
    })
  })

  it('vuelve al login si el logout remoto falla', async () => {
    const service = createAuthService(
      createManager({
        getUser: vi.fn(async () => makeUser()),
        signoutRedirect: vi.fn(async () => {
          throw new Error('logout remoto fallido')
        }),
      }),
      config,
    )

    render(<AuthGate service={service} />)

    fireEvent.click(await screen.findByRole('button', { name: 'Cerrar sesión' }))

    expect((await screen.findByRole('alert')).textContent).toBe(
      'No se ha podido cerrar la sesión en Keycloak.',
    )
    expect(
      screen.getByRole('button', { name: 'Iniciar sesión' }),
    ).toBeDefined()
  })
})

function authenticatedService() {
  return createAuthService(
    createManager({ getUser: vi.fn(async () => makeUser()) }),
    config,
  )
}

function validResult(
  overrides: Partial<AnonymizationResult> = {},
): AnonymizationResult {
  return {
    status: 'validado',
    confidence: 0.93,
    anonymized_text: 'Paciente: [PACIENTE]. DNI: [DNI].',
    entities_count: { PERSON: 1, ES_DNI: 1 },
    reason: null,
    ...overrides,
  }
}

function selectTxt(contents = 'Informe inventado de [PACIENTE].') {
  fireEvent.change(screen.getByLabelText('Documento (.txt)'), {
    target: {
      files: [
        new File([contents], 'documento-sintetico.txt', {
          type: 'text/plain',
        }),
      ],
    },
  })
}

async function submitUpload(name = 'Subir y anonimizar') {
  await act(async () => {
    fireEvent.click(screen.getByRole('button', { name }))
  })
}

describe('AuthGate — flujo E2E', () => {
  it('sube, valida y abre la conversación solo con el texto anonimizado', async () => {
    const result = validResult()
    anonymizeTextMock.mockResolvedValue(result)
    sendConversationMock.mockResolvedValue({
      answer: 'Respuesta inventada.',
      truncated: false,
    })

    render(<AuthGate service={authenticatedService()} />)

    expect(
      await screen.findByRole('heading', { name: 'Subir documento' }),
    ).toBeDefined()
    expect(screen.queryByRole('button', { name: 'Conversación' })).toBeNull()

    selectTxt()
    await submitUpload()

    expect(
      await screen.findByRole('heading', { name: 'Documento validado' }),
    ).toBeDefined()
    expect(anonymizeTextMock).toHaveBeenCalledWith(
      'Informe inventado de [PACIENTE].',
    )
    expect(
      screen.getByRole('button', { name: 'Conversación' }),
    ).toBeDefined()

    fireEvent.click(
      screen.getByRole('button', { name: 'Continuar a la conversación' }),
    )

    expect(
      await screen.findByRole('heading', { name: 'Conversación' }),
    ).toBeDefined()
    expect(
      screen
        .getByRole('button', { name: 'Conversación' })
        .getAttribute('aria-current'),
    ).toBe('page')

    fireEvent.change(screen.getByRole('textbox', { name: 'Tu pregunta' }), {
      target: { value: '¿Qué significa el resultado?' },
    })
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Enviar' }))
    })

    expect(sendConversationMock).toHaveBeenCalledWith({
      documents: [{ text: result.anonymized_text }],
      messages: [{ role: 'user', content: '¿Qué significa el resultado?' }],
    })
    expect(await screen.findByText('Respuesta inventada.')).toBeDefined()

    // Volver a «Documento» desmonta la conversación y pierde su hilo.
    fireEvent.click(screen.getByRole('button', { name: 'Documento' }))
    expect(
      screen.getByRole('heading', { name: 'Subir documento' }),
    ).toBeDefined()
    expect(
      screen.getByRole('button', { name: 'Conversación' }),
    ).toBeDefined()

    fireEvent.click(screen.getByRole('button', { name: 'Conversación' }))
    expect(
      await screen.findByRole('heading', { name: 'Conversación' }),
    ).toBeDefined()
    expect(screen.queryByText('¿Qué significa el resultado?')).toBeNull()
  })

  it.each([
    [
      'retenido',
      'Documento retenido',
      'No se ha podido procesar el documento con garantías. Puedes intentarlo con otra copia.',
      'baja_confianza',
    ],
    [
      'ilegible',
      'Documento ilegible',
      'El documento no contiene texto que se pueda leer. Puedes intentarlo con otro fichero.',
      'texto_vacio',
    ],
  ] as const)(
    'no ofrece conversación con un resultado %s',
    async (status, heading, message, reason) => {
      anonymizeTextMock.mockResolvedValue(
        validResult({
          status,
          confidence: status === 'retenido' ? 0.42 : 1,
          anonymized_text: null,
          entities_count: {},
          reason,
        }),
      )

      render(<AuthGate service={authenticatedService()} />)
      await screen.findByRole('heading', { name: 'Subir documento' })

      selectTxt()
      await submitUpload()

      expect(await screen.findByRole('heading', { name: heading })).toBeDefined()
      expect(screen.getByText(message)).toBeDefined()
      expect(screen.queryByRole('button', { name: 'Conversación' })).toBeNull()
      expect(
        screen.queryByRole('button', { name: 'Continuar a la conversación' }),
      ).toBeNull()

      fireEvent.click(
        screen.getByRole('button', { name: 'Probar con otro documento' }),
      )
      expect(
        await screen.findByRole('heading', { name: 'Subir documento' }),
      ).toBeDefined()
    },
  )

  it('descarta el flujo y vuelve al login al caducar la sesión', async () => {
    anonymizeTextMock.mockResolvedValue(validResult())

    render(<AuthGate service={authenticatedService()} />)
    await screen.findByRole('heading', { name: 'Subir documento' })

    selectTxt()
    await submitUpload()
    expect(
      await screen.findByRole('heading', { name: 'Documento validado' }),
    ).toBeDefined()

    act(() => {
      window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT))
    })

    expect(
      await screen.findByRole('heading', { name: 'Iniciar sesión' }),
    ).toBeDefined()
    expect(screen.queryByText('Documento validado')).toBeNull()
    expect(screen.queryByRole('button', { name: 'Documento' })).toBeNull()
  })
})
