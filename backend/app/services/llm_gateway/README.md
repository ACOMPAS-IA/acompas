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

## Proveedor simulado

`LLMGateway(provider=...)` acepta cualquier objeto que cumpla `LLMProvider` (`complete(request, settings) -> LLMResponse`). Los tests lo usan para no depender de red ni de clave.
