# Cliente de API del frontend (ACO-019)

Contrato de integración para ACO-032 y para cualquier llamada autenticada al
backend desde el frontend.

## Qué hace el cliente

`frontend/src/api/client.ts` exporta `apiRequest`:

```ts
apiRequest<T>(path, init?, { allowedDetails })
```

Antes de cada petición:

1. Llama a `getAccessToken()` de `frontend/src/auth/authService.ts`.
2. Si no hay token, emite `acompas:session-expired`, no llama a `fetch` y lanza
   `SessionExpiredError`.
3. Añade `Authorization: Bearer <token>`, `Accept: application/json`,
   `credentials: 'omit'` y `cache: 'no-store'`.

El token lo obtiene siempre `getAccessToken()`. El componente que llama no debe
leer `sessionStorage`, construir la cabecera `Authorization` ni guardar el token.

## Errores

- `SessionExpiredError`: no había token o el backend devolvió 401. La sesión se
  ha limpiado y la interfaz vuelve al login.
- `ApiError`: error HTTP o de red. Tiene `status` y `detail`.
- `detail` solo conserva los códigos declarados por la petición. Cualquier otro
  código, cuerpo no JSON o error de red se convierte en `request_failed`.

Códigos de autenticación admitidos siempre: `unauthorized`, `forbidden`,
`auth_unavailable`.

Nunca se incluyen en el error el token, sus claims, la cabecera ni el cuerpo
original. Tampoco se escriben en logs.

## Conversación

`frontend/src/api/conversation.ts` ya usa `apiRequest`. `ConversationPage`
recibe `sendConversation` como función por defecto, así que sus envíos quedan
autenticados sin cambiar la página.

## Añadir una llamada nueva (ACO-032)

Para la API de anonimización de ACO-024:

```ts
import { apiRequest } from './client.ts'

const ANONYMIZATION_ALLOWED_DETAILS = [
  'invalid_request',
  'text_too_long',
  'anonymization_not_configured',
] as const

const result = await apiRequest<AnonymizationResult>(
  '/api/anonymization',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  },
  { allowedDetails: ANONYMIZATION_ALLOWED_DETAILS },
)
```

`AnonymizationResult` y sus estados (`validado`, `retenido`, `ilegible`) son los
de ACO-024. No hace falta modificar `client.ts` para añadir un endpoint.

Para los errores de conversación, `conversation.ts` declara los códigos de
ACO-030: `llm_not_configured`, `llm_busy`, `llm_unavailable`, `llm_timeout` y
`llm_error`.

## Proxy de desarrollo

El frontend usa rutas relativas `/api/...`. Vite las reenvía al backend:

- ejecución local con `npm run dev`: `http://localhost:8000` por defecto;
- Docker Compose: `API_PROXY_TARGET=http://backend:8000` en el servicio
  `frontend`.

No se configura CORS en el backend: el navegador habla siempre con
`http://localhost:5173`, que es el mismo origen.

## Sesión caducada

`frontend/src/auth/sessionExpiry.ts` emite `acompas:session-expired`.
`useAuthSession` escucha el evento, pasa a `anonymous` una sola vez, muestra
«La sesión ha caducado. Vuelve a iniciar sesión.» y llama a `clearSession()`,
que elimina la sesión local sin redirigir a Keycloak. Un `getUser()` tardío no
puede restaurar la sesión porque el hook invalida su generación.

## Pruebas

Los tests usan Vitest y jsdom. `fetch`, `getAccessToken` y el gestor OIDC se
sustituyen: no se usa red, Keycloak ni el backend real. Los tokens y textos son
sintéticos.
