# Conversación sobre documento

Flujo conversacional mínimo de ACOMPAS (ACO-030): recibe los documentos anonimizados y la conversación, construye los mensajes con el system prompt de ACO-029 y llama a Claude a través del LLM gateway de ACO-027 (ADR-006). El contrato completo está en la ficha `docs/aco/ACO-030.md`, secciones 7 y 8.

El endpoint `POST /api/conversation` vive en `backend/app/api/conversation.py`.

## Uso

```python
from app.services.conversation import ChatMessage, ConversationRequest, ConversationService, DocumentInput
from app.services.llm_gateway import LLMGateway

response = ConversationService(LLMGateway()).answer(
    ConversationRequest(
        documents=[DocumentInput(text="...")],
        messages=[ChatMessage(role="user", content="...")],
    )
)
response.answer, response.truncated
```

`answer()` lanza `LLMGatewayError` sin cambiarlo. Una respuesta vacía del modelo se trata como `provider_error`.

## Sin estado

El backend no guarda nada de la conversación. En cada petición el cliente envía los documentos y la conversación completa hasta la nueva pregunta. Ni el servicio ni el endpoint registran el contenido de documentos, preguntas o respuestas (R-04): el registro de metadatos de cada llamada lo hace el gateway.

## Límites

Constantes de `models.py`. Una petición fuera de ellos se rechaza al validarla, sin llamar al gateway (en HTTP, con 422).

| Constante | Valor |
| --- | --- |
| `MAX_DOCUMENTS` | 3 |
| `MAX_DOCUMENT_CHARS` | 30.000 por documento |
| `MAX_MESSAGES` | 21 (alternando `user` y `assistant`, empezando y terminando en `user`) |
| `MAX_QUESTION_CHARS` | 2.000 por mensaje `user` |
| `MAX_ANSWER_CHARS` | 8.000 por mensaje `assistant` |

## Mensajes al gateway

- `system` es `load_system_prompt().text`.
- El primer mensaje `user` contiene cada documento entre `<documento_clinico>` y `</documento_clinico>`, separados por una línea en blanco, y después la primera pregunta.
- El resto de mensajes pasa en el mismo orden.
- `max_output_tokens` no se envía: se usa el de la configuración del gateway.

## Neutralización de delimitadores

`neutralize_delimiters()` se aplica a cada documento y a cada mensaje `user`, para que ningún texto pueda cerrar o abrir un documento (ACO-029 P3; R-26). Sustituye por `(documento_clinico)` toda etiqueta que cumpla este patrón, sin distinguir mayúsculas:

```text
[<＜﹤] \s* [/／]? \s* documento [\s_-]+ cl(í|i|i + tilde combinada)nico [sin <>＜＞﹤﹥]{0,40} [>＞﹥]
```

- Corchetes angulares normales, de ancho completo (U+FF1C, U+FF1E) y de forma pequeña (U+FE64, U+FE65).
- Barra normal o de ancho completo (U+FF0F).
- Entre «documento» y «clinico», guion bajo, guion o espacios; «clinico» con o sin tilde.
- Tras el nombre, como máximo 40 caracteres de atributos, sin ningún corchete angular. Una etiqueta sin cerrar seguida de texto no se sustituye, para no borrar texto clínico hasta un `>` lejano.

No normaliza el texto (ni NFKC ni otra forma) y no cambia nada que no sea la etiqueta: un texto como «PSA < 4» o «CA 19-9 > 37» llega intacto.

## Errores HTTP

| Código del gateway | HTTP | `detail` |
| --- | --- | --- |
| `not_configured` | 503 | `llm_not_configured` |
| `rate_limit` | 503 | `llm_busy` |
| `unavailable`, `auth` | 503 | `llm_unavailable` |
| `timeout` | 504 | `llm_timeout` |
| `invalid_request`, `provider_error` | 502 | `llm_error` |
| (respuesta vacía del modelo) | 502 | `llm_error` |

El cuerpo es `{"detail": "<código>"}`, sin el mensaje del gateway, el código HTTP del proveedor ni el identificador de petición.

## Tests

`get_llm_gateway` es una dependencia de FastAPI: los tests la sustituyen con `app.dependency_overrides` por `LLMGateway(provider=...)` con un proveedor simulado, sin red ni clave. `tests/conversation/test_live.py` hace una llamada real y se omite salvo con `ACOMPAS_LLM_LIVE=1`, `ANTHROPIC_API_KEY` y `LLM_MODEL`.
