# 07 — INTERCAMBIO

> Pieza del arnés de ACOMPAS. Es una capa derivada: no decide, no es fuente de verdad y se regenera, no se edita a mano. Ante cualquier conflicto prevalece la fuente oficial. Las versiones exactas de las fuentes constan en `docs/arnes/MANIFIESTO.md`.

## Objetivo y alcance

Contratos entre módulos, APIs y datos que se necesitan para integrar. Solo recoge contratos que existen o que una fuente define de forma explícita. **Que falte un contrato no autoriza a inventarlo:** si un ACO lo necesita y no está definido, el ACO responsable lo define y documenta en su PR. Si afecta a otro ACO, es BLOQUEO o FUERA DE ALCANCE (`AGENTS.md`).

## Qué no contiene

- Esquemas JSON, endpoints ni firmas concretas que ninguna fuente fija. Los contratos que definen las fichas se materializan en el código y en la documentación de cada ACO, y esta pieza no los reproduce.
- El modelo completo de entidades: está en 02-DOMINIO.

## Fuentes

- **Normativas:** Arquitectura del Sistema (§3, §4, §5, §8, §9, §11, §13); ADR-001, ADR-003, ADR-004, ADR-005, ADR-006, ADR-009, ADR-011 y ADR-012.
- **Derivadas:** Modelo E/R (§2, §3, §4); Casos de Uso (UC-03, UC-07, UC-09); Fichas ACO-014, 019, 020, 021, 023, 024, 025, 027, 028, 030, 032 y 051.

## 1. Contratos transversales (definidos)

| Contrato | Definición | Fuente |
|---|---|---|
| Autenticación en cada petición | Todas las peticiones al API llevan un JWT firmado con expiración, emitido por Keycloak (OIDC). El backend lo valida, rechaza los tokens ausentes o inválidos y aplica la autorización por rol (paciente o administrador) y por propiedad del recurso. | ADR-011; Arquitectura §3, §11; ACO-014 |
| Identidad | El backend recibe del token la identidad del paciente como UUID. El email solo se usa para comprobar la lista blanca en el alta y no se persiste asociado al paciente. | ADR-001; ADR-009; UC-03 |
| Lista blanca | Antes de que Keycloak resuelva o cree el UUID, se comprueba que el email está en EMAIL_AUTORIZADO. La comprobación es aplicativa (sin FK). El mecanismo concreto está abierto. | ADR-009; Modelo E/R §3; UC-03 |
| Paso obligatorio por el gateway | Conversación → LLM gateway → Claude API. Ninguna otra ruta llama a Claude API. Cada llamada genera un registro de consumo (paciente, tokens, fecha). | ADR-006; Arquitectura §8; Modelo E/R CONSUMO_LLM |
| Datos que recibe el LLM | Solo el texto **anonimizado** del documento, nunca el original. | ADR-005; Arquitectura §3, §4 |
| Secretos | La API key del proveedor LLM se obtiene de la configuración segura del backend y nunca viaja al navegador ni aparece en las respuestas HTTP o en los logs. | ACO-028 |
| Origen de la respuesta | La respuesta indica la fuente recuperada (fragmento del documento, glosario o publicación) o que procede del conocimiento interno del LLM. | Arquitectura §6, §11; UC-09 |

## 2. Pipeline de anonimización (Sprint 1)

| Interfaz | Qué está definido | Qué no está definido | Fuente |
|---|---|---|---|
| Servicio de anonimización (ACO-020) | Contrato de entrada y salida **sobre texto**, invocable desde Python y con pruebas unitarias. No introduce persistencia del original. | Forma concreta del contrato: la fija ACO-020 en el repositorio. | ACO-020 |
| Analizador (ACO-021) | Función de construcción del `AnalyzerEngine` reutilizable (Presidio + `TransformersNlpEngine`, modelo `BSC-NLP4BIA/bsc-bio-ehr-es-meddocan`, idioma `es`). Devuelve detecciones con la **puntuación** de Presidio. Mapeo explícito entre categorías MEDDOCAN y tipos de entidad, distinguiendo lo detectable de lo que se anonimiza. | Qué entidades se anonimizan (ACO-023). | ACO-021 §3, §7–§9 |
| Política y umbral (ACO-023) | Separa lo detectado de lo anonimizado. El umbral es configurable y está documentado. Un documento que no supera la validación no pasa al flujo posterior. | Valor del umbral; tratamiento del documento retenido. | ACO-023; ADR-003 |
| API de anonimización (ACO-024) | Interfaz HTTP **interna** del backend: entrada de texto y salida anonimizada conforme al contrato de ACO-020, con errores y validaciones básicas. **No devuelve el texto original.** | Ruta, método y esquema: los define y documenta ACO-024. | ACO-024 |
| No persistencia (ACO-025) | El original no se escribe en la base de datos ni en almacenamiento persistente, ni en logs. La interfaz devuelve solo lo necesario para continuar el flujo. | — | ACO-025; ADR-005 |
| Etiquetas | Etiquetas `[TIPO_n]` numeradas por documento (p. ej. `[PACIENTE]`, `[MÉDICO_1]`, `[HOSPITAL]`, `[FECHA_NACIMIENTO]`), sin valor original. | Agrupación de variantes de un nombre dentro del documento. | ADR-012; Arquitectura §4 |

## 3. Integración del Sprint 1

| Interfaz | Qué está definido | Fuente |
|---|---|---|
| Cliente de API del frontend (ACO-019) | Cliente centralizado que incluye la autenticación. Su **contrato de integración se documenta para ACO-032**. | ACO-019 |
| LLM gateway v0 (ACO-027) | **Contrato mínimo entre la conversación y el proveedor LLM**, con una integración mínima con Claude para la demo y gestión de configuración y secretos compatible con ACO-028. | ACO-027 (criterios pendientes de revisión) |
| Conversación (ACO-030) | El contexto documental llega al LLM de forma controlada, y la respuesta se muestra en la interfaz prevista. | ACO-030 (criterios pendientes de revisión) |
| Flujo E2E (ACO-032) | Integra los contratos entre frontend, API, anonimización y conversación: login → acceso autorizado → documento sintético → anonimización → conversación → respuesta. | ACO-032 |
| Datos sintéticos (ACO-051) | `load_document(nombre)`, `load_manifest()` y `count_occurrences(...)` en `backend/tests/synthetic_data/__init__.py`. Formato del manifiesto en 06-SEMILLA. | ACO-051 §3, §7, B4 |

Los puntos de entrega entre personas y el orden en que deben acordarse estos contratos están en 08-PLAN.

## 4. Datos persistidos que intercambian los módulos (posterior a S1)

*(Modelo E/R; detalle en 02-DOMINIO)*

- **DOCUMENTO:** nombre genérico, `ruta_almacen` del anonimizado, `hash_fichero` único por paciente, `estado_anon` y `confianza_automatica`. *(ADR-005, ADR-012)*
- **ETIQUETA_ANONIMIZACION:** `numero` por documento, `fuente` ∈ {`presidio`, `paciente`}, `confirmada`; sin valor original. *(ADR-003, ADR-012)*
- **Derecho al olvido:** secuencia de borrado de referencia *(Modelo E/R §4; UC-07; ADR-001)*: MENSAJE → SESION → ETIQUETA_ANONIMIZACION → DOCUMENTO (y su anonimizado) → PREFERENCIA_RESUMEN → CONSUMO_LLM → SOLICITUD_DESBLOQUEO_CREDITO → CREDITO_PACIENTE → AUDITORIA del paciente → PACIENTE.activo = false → cuenta en Keycloak (Admin API) → evento final en AUDITORIA.

## 5. Sistemas externos

| Sistema | Intercambio | Fuente |
|---|---|---|
| Keycloak | OIDC (login, JWT); Admin API para el borrado de la cuenta | ADR-001, ADR-011; UC-07 |
| Claude API | Solo a través del gateway, con texto anonimizado; garantía contractual de no retención ni uso para entrenamiento | ADR-006; Arquitectura §11, §13 |
| PubMed Central | API E-utilities, ingesta periódica (Fase 1.5) | Arquitectura §5 |
| OCR | Ninguno externo: Tesseract local (S2) | ADR-004 |

## Cuestiones abiertas

| Cuestión | Fuente |
|---|---|
| Encaje mínimo y alcance del LLM gateway en el Sprint 1 (contrato de ACO-027) | Plan de Trabajo §9; ACO-027 |
| Contrato de la API de conversación entre el cliente (019) y la conversación (030), y entre la API de anonimización (024) y la conversación: deben acordarse antes de 032 y no están definidos en ninguna fuente | ACO-019; ACO-032; Documento Operativo §11 |
| Qué devuelve el flujo cuando el documento se retiene | Plan de Trabajo §9; ACO-023 |
| Formatos de entrada del Sprint 1 (texto frente a PDF o imagen) | ACO-020; ACO-051 P1; Wireframes, pantalla 3 |
| Mecanismo de la lista blanca y su conexión con Keycloak; Admin API y su autenticación | ADR-009, ADR-001 (Fuera de esta decisión) |
| Claims y expiración del JWT | ADR-011 (Fuera de esta decisión) |
| Semántica de posicion_inicio y posicion_fin | Modelo E/R |
| Diseño definitivo del derecho al olvido y del registro de auditoría | Arquitectura §16 nº 3–4 |
