# LLM gateway

Punto único de paso hacia Claude API (ADR-006). Ningún otro módulo de `backend/app` importa el SDK `anthropic`: solo `anthropic_provider.py`. El contrato completo está en la ficha `docs/aco/ACO-027.md`, secciones 7 y 8.

## Uso

```python
from app.services.llm_gateway import LLMGateway, LLMMessage, LLMRequest

response = LLMGateway().complete(
    LLMRequest(
        system="...",
        messages=[LLMMessage(role="user", content="...")],
    )
)
response.text, response.input_tokens, response.output_tokens, response.stop_reason
```

La llamada es síncrona y sin streaming. Una petición sin mensajes, con un texto vacío, con el primer o el último mensaje de `assistant` o con `max_output_tokens` no positivo se rechaza con `ValidationError` al construirla.

## Configuración

Se lee del entorno en cada llamada, no al importar ni al arrancar la aplicación. Una variable vacía equivale a no definida.

| Variable | Obligatoria | Por defecto |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | Para llamar a la API | — |
| `LLM_MODEL` | Para llamar a la API | — |
| `LLM_MAX_OUTPUT_TOKENS` | No | 1024 |
| `LLM_TIMEOUT_SECONDS` | No | 60 |
| `LLM_MAX_RETRIES` | No | 2 |

`config.get_api_key()` es la única función que lee la clave. Sin clave o sin modelo, la aplicación arranca igual y solo falla la llamada al gateway, con `not_configured`.

`load_settings()` aplica una lista de permitidas (ADR-015): cualquier variable de entorno `ANTHROPIC_*` distinta de `ANTHROPIC_API_KEY` hace que la llamada falle con `not_configured`, sin llamar al proveedor. Se registra solo el nombre de la variable, nunca su valor. La comprobación se hace en cada llamada, no al importar.

## Cliente

El cliente se construye con `api_key`, `base_url="https://api.anthropic.com"`, `open_telemetry=False` y `http_client=anthropic.DefaultHttpxClient(trust_env=False, transport=httpx2.HTTPTransport(trust_env=False))`, conservando `timeout` y `max_retries`. El transporte explícito es necesario porque el `DefaultHttpxClient` de `anthropic` 1.17.0 construye mounts de proxy desde el entorno aunque reciba `trust_env=False`; con él se desactivan de verdad los proxies y los certificados del entorno. No se aceptan `ANTHROPIC_BASE_URL` ni cabeceras alternativas.

## Errores

Todo fallo llega como `LLMGatewayError`, con `code` (`LLMErrorCode`), `status_code` y `request_id` del proveedor si existen. El mensaje es fijo para cada código y no incluye la clave, el contenido de la petición ni el mensaje del proveedor. La excepción original no se encadena.

| Código | Cuándo |
| --- | --- |
| `not_configured` | Falta la clave o el modelo, o un número de la configuración no es válido. |
| `auth` | HTTP 401 o 403. |
| `rate_limit` | HTTP 429. |
| `timeout` | Se agota el tiempo máximo, o HTTP 408. |
| `unavailable` | Sin conexión, o HTTP 5xx (incluido 529, saturado). |
| `invalid_request` | HTTP 400, 404, 413 o 422 (por ejemplo, modelo inexistente). |
| `provider_error` | Cualquier otro error del SDK. |

## Registro

Logger `app.services.llm_gateway`, nivel INFO, una línea por llamada:

- correcta: modelo, tokens de entrada y salida, motivo de fin, duración en milisegundos y los 12 primeros caracteres de la huella SHA-256 de `system`;
- fallida: código, código HTTP e identificador de petición.

Nunca el contenido de `system`, de los mensajes ni de la respuesta. No se activa el registro de depuración del SDK (`ANTHROPIC_LOG`).

Al arrancar, `app.logging.configure_logging()` deja el logger de la aplicación en INFO y los loggers `anthropic`, `httpx2` y `httpcore2` en nivel efectivo INFO o superior, con `propagate=True`. Así se ve la línea INFO del gateway y los avisos y errores del SDK siguen llegando, pero el cuerpo de las peticiones se queda en DEBUG y no se emite.

## Verificación y rotación

`scripts/check-secrets.sh` comprueba que el prefijo de las claves de Anthropic no está en los archivos rastreados, el índice ni el historial, con la excepción explícita de las menciones documentales de ADR-015 y 09-TESTS; además busca cadenas con forma de clave real sin excepciones, comprueba `.env`, `.env.example`, Compose y el frontend. No lee archivos no versionados.

El procedimiento manual de rotación está en el `README.md` y el `README.es.md` de la raíz.

## Proveedor simulado

`LLMGateway(provider=...)` acepta cualquier objeto que cumpla `LLMProvider` (`complete(request, settings) -> LLMResponse`). Los tests lo usan para no depender de red ni de clave.
