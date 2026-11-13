# 07 — INTERCAMBIO

> Pieza del arnés de ACOMPAS. Es una capa derivada: no decide, no es fuente de verdad y se regenera, no se edita a mano. Ante cualquier conflicto prevalece la fuente oficial. Las versiones exactas de las fuentes constan en `docs/arnes/MANIFIESTO.md`.

## Objetivo y alcance

Contratos entre módulos, APIs y datos que se necesitan para integrar. Solo recoge contratos que existen o que una fuente define de forma explícita. **Que falte un contrato no autoriza a inventarlo:** si un ACO lo necesita y no está definido, el ACO responsable lo define y documenta en su PR. Si afecta a otro ACO, es BLOQUEO o FUERA DE ALCANCE (`AGENTS.md`).

## Qué no contiene

- Esquemas JSON, endpoints ni firmas concretas que ninguna fuente fija. Los contratos que definen las fichas se materializan en el código y en la documentación de cada ACO, y esta pieza no los reproduce.
- El modelo completo de entidades: está en 02-DOMINIO.

## Fuentes

- **Normativas:** Arquitectura del Sistema (§3, §4, §5, §6, §8, §11, §13, §16); ADR-001, ADR-003, ADR-004, ADR-005, ADR-006, ADR-009, ADR-011, ADR-012, ADR-013, ADR-014, ADR-015, ADR-016, ADR-017 y ADR-018.
- **Derivadas:** Modelo E/R (§2, §3, §4); Casos de Uso (UC-03, UC-07, UC-09); Fichas ACO-012, 014, 015, 019, 020, 021, 023, 024, 025, 027, 028, 030, 032 y 051.

## 1. Contratos transversales (definidos)

| Contrato | Definición | Fuente |
|---|---|---|
| Autenticación en cada petición | Todas las peticiones al API llevan un JWT firmado con expiración, emitido por Keycloak (OIDC). El backend lo valida, rechaza los tokens ausentes o inválidos y aplica la autorización por rol (paciente o administrador) y por propiedad del recurso. El realm no emite refresh tokens offline: `offline_access` no está en el rol por defecto. | ADR-011; ADR-016; ADR-018; Arquitectura §3, §11; ACO-014 |
| Identidad | El backend recibe del token la identidad del paciente como UUID y, si el cliente pide el scope `email`, el email como claim opcional. El email solo se usa para comprobar la lista blanca en cada petición protegida y no se persiste asociado al paciente. | ADR-001; ADR-009; ADR-017; UC-03 |
| Lista blanca | La lista vive en `EMAILS_AUTORIZADOS` (`.env` local no versionado) y se comprueba en el backend en cada petición protegida, después de validar el JWT y el rol de aplicación. Token sin email, email fuera de la lista o lista ausente o vacía producen 403 con cuerpo genérico (`forbidden`). La comparación es exacta tras `strip()` y minúsculas. La lista no se devuelve por ningún endpoint ni se escribe en logs. La tabla `EMAIL_AUTORIZADO` vuelve en el Sprint 2. | ADR-009; ADR-017; ACO-015 §8; Modelo E/R §3 |
| Configuración del realm posterior a la importación | El JSON declara `defaultRole` y no incluye `offline_access` en el rol por defecto. Como el perfil de usuario y el composite no viajan en el JSON, tras cada importación limpia se ejecuta `scripts/apply-realm-config.sh` (perfil de email y rol por defecto) y después `scripts/check-realm.sh`, que comprueba el rol efectivo y `email.permissions.edit = ["admin"]`. Los scripts son idempotentes, solo aceptan `localhost` o `127.0.0.1` y no registran credenciales. | ADR-016; ADR-017; ADR-018; ACO-012 P16–P18 |
| Paso obligatorio por el gateway | Conversación → LLM gateway → Claude API. Ninguna otra ruta llama a Claude API. Cada llamada genera un registro de consumo (paciente, tokens, fecha). | ADR-006; Arquitectura §8; Modelo E/R CONSUMO_LLM |
| Datos que recibe el LLM | Solo el texto **anonimizado** del documento, nunca el original. | ADR-005; Arquitectura §3, §4 |
| Secretos | La API key del proveedor LLM se obtiene de la configuración segura del backend y nunca viaja al navegador ni aparece en las respuestas HTTP o en los logs. Solo el servicio `backend` recibe la variable, desde un `.env` local no versionado; `load_settings()` rechaza cualquier variable `ANTHROPIC_*` distinta de la clave, y el cliente desactiva el entorno (`trust_env=False`) y la telemetría de contenido. | ADR-015; ACO-028 |
| Origen de la respuesta | La respuesta indica la fuente recuperada (fragmento del documento, glosario o publicación) o que procede del conocimiento interno del LLM. | Arquitectura §6, §11; UC-09 |

## 2. Pipeline de anonimización (Sprint 1)

| Interfaz | Qué está definido | Qué no está definido | Fuente |
|---|---|---|---|
| Servicio de anonimización (ACO-020) | Contrato de entrada y salida **sobre texto**, invocable desde Python y con pruebas unitarias. No introduce persistencia del original. | Forma concreta del contrato: la fija ACO-020 en el repositorio. | ACO-020 |
| Analizador (ACO-021) | Función de construcción del `AnalyzerEngine` reutilizable (Presidio + `TransformersNlpEngine`, modelo `BSC-NLP4BIA/bsc-bio-ehr-es-meddocan`, idioma `es`). Devuelve detecciones con la **puntuación** de Presidio. Mapeo explícito entre categorías MEDDOCAN y tipos de entidad, distinguiendo lo detectable de lo que se anonimiza. ACO-022 corrige el mapeo para conservar el rol de las personas y añade la asignación de rol por contexto, con la etiqueta genérica como caída, y los reconocedores propios (DNI y NIE con letra de control, número de historia por contexto, nombres tras etiqueta, dirección completa, firmas). | Lista concreta de reconocedores, filtros y términos permitidos (fichas de ACO-022 y ACO-023). | ACO-021 §3, §7–§9; ADR-013 |
| Política y umbrales (ACO-023) | Separa lo detectado de lo anonimizado según la política de ADR-013 (03-REGLAS R-44…R-48) y numera con la agrupación de menciones de ADR-014 (R-53), salvo las que no se agrupan, que reciben número propio; la asignación y la propagación del rol son de ACO-022. Dos umbrales configurables: el de hallazgo y el de documento (R-13). Los tests leen los valores de la configuración. Un documento retenido no pasa al flujo posterior ni se guarda; un documento ilegible no se procesa; los dos producen un aviso al paciente con motivos distintos (R-49, R-50). | Fórmula de la confianza del documento: la define y documenta ACO-023. Texto de los avisos. | ACO-023; ADR-013; ADR-014; ADR-003; Arquitectura §4 |
| API de anonimización (ACO-024) | Interfaz HTTP **interna** del backend: entrada de texto y salida anonimizada conforme al contrato de ACO-020, con errores y validaciones básicas. **No devuelve el texto original.** | Ruta, método y esquema: los define y documenta ACO-024. | ACO-024 |
| No persistencia (ACO-025) | El original no se escribe en la base de datos ni en almacenamiento persistente, ni en logs. La interfaz devuelve solo lo necesario para continuar el flujo. | — | ACO-025; ADR-005 |
| Etiquetas | Etiquetas `[TIPO_n]` numeradas por documento (p. ej. `[PACIENTE]`, `[SANITARIO_1]`, `[FAMILIAR_1]`, `[PERSONA_1]`, `[HOSPITAL]`, `[FECHA_NACIMIENTO]`), sin valor original. Por rol cuando se puede determinar; si no, la genérica de persona. El rol se propaga entre las menciones del mismo nombre dentro del documento (R-53). | Nombre exacto de la etiqueta genérica y catálogo de TIPO_ETIQUETA. | ADR-012; ADR-013; ADR-014; Arquitectura §4 |

## 3. Integración del Sprint 1

| Interfaz | Qué está definido | Fuente |
|---|---|---|
| Cliente de API del frontend (ACO-019) | Cliente centralizado que incluye la autenticación. Su **contrato de integración se documenta para ACO-032**. | ACO-019 |
| LLM gateway v0 (ACO-027) | **Contrato mínimo entre la conversación y el proveedor LLM**, con una integración mínima con Claude para la demo y gestión de configuración y secretos conforme a ADR-015. | ACO-027 (criterios confirmados en la revisión de la PR #70) |
| Conversación (ACO-030) | El contexto documental llega al LLM de forma controlada, y la respuesta se muestra en la interfaz prevista. | ACO-030 (criterios pendientes de revisión) |
| Flujo E2E (ACO-032) | Integra los contratos entre frontend, API, anonimización y conversación: login → acceso autorizado → documento sintético → anonimización → conversación → respuesta. | ACO-032 |
| Datos sintéticos (ACO-051) | `load_document(nombre)`, `load_manifest()` y `count_occurrences(...)` en `backend/tests/synthetic_data/__init__.py`. Formato del manifiesto en 06-SEMILLA. | ACO-051 §3, §7, B4 |

Los puntos de entrega entre personas y el orden en que deben acordarse estos contratos están en 08-PLAN.

## 4. Datos persistidos que intercambian los módulos (posterior a S1)

*(Modelo E/R; detalle en 02-DOMINIO)*

- **DOCUMENTO:** nombre genérico, `ruta_almacen` del anonimizado, `hash_fichero` único por paciente, `estado_anon` (`pendiente` o `validado`) y `confianza_automatica`. *(ADR-005, ADR-012; Modelo E/R)* Un documento retenido no se guarda: solo deja un registro de auditoría sin contenido ni nombre del fichero (fecha, tipo de documento, motivo) *(ADR-013)*.
- **ETIQUETA_ANONIMIZACION:** `numero` por documento, `tipo_entidad` con los códigos del Modelo E/R, `fuente` ∈ {`presidio`, `paciente`}, `confirmada`; sin valor original. *(ADR-003, ADR-012)*
- **SOLICITUD_DESBLOQUEO_CREDITO:** `motivo` (texto libre, opcional, lo escribe el paciente) y `motivo_resolucion` (texto libre; obligatorio al denegar y opcional al aprobar); el paciente ve el motivo de la resolución en el detalle de su solicitud. *(Modelo E/R; Wireframes 8 y 9)* No hay límite, validación ni anonimización definidos para esos textos (ver Cuestiones abiertas).
- **Derecho al olvido:** secuencia de borrado de referencia *(Modelo E/R §4; UC-07; ADR-001)*: MENSAJE → SESION → ETIQUETA_ANONIMIZACION → DOCUMENTO (y su anonimizado) → PREFERENCIA_RESUMEN → CONSUMO_LLM → SOLICITUD_DESBLOQUEO_CREDITO → CREDITO_PACIENTE → AUDITORIA del paciente → PACIENTE.activo = false → cuenta en Keycloak (Admin API) → evento final en AUDITORIA.

## 5. Sistemas externos

| Sistema | Intercambio | Fuente |
|---|---|---|
| Keycloak | OIDC (login, JWT); Admin API acotada a los scripts de configuración del realm (perfil de email y rol por defecto, en local/demo) y al borrado de la cuenta | ADR-001, ADR-011, ADR-017, ADR-018; UC-07 |
| Claude API | Solo a través del gateway, con texto anonimizado; garantía contractual de no retención ni uso para entrenamiento | ADR-006; Arquitectura §11, §13 |
| PubMed Central | API E-utilities, ingesta periódica (Fase 1.5) | Arquitectura §5 |
| OCR | Ninguno externo: Tesseract local (S2) | ADR-004 |

## Cuestiones abiertas

| Cuestión | Fuente |
|---|---|
| Encaje mínimo y alcance del LLM gateway en el Sprint 1 (contrato de ACO-027) | Arquitectura §16 nº 12; ACO-027 |
| Contrato de la API de conversación entre el cliente (019) y la conversación (030), y entre la API de anonimización (024) y la conversación: deben acordarse antes de 032 y no están definidos en ninguna fuente | ACO-019; ACO-032; Documento Operativo §11 |
| Texto de los avisos al paciente (documento retenido e ilegible) | ADR-013 (Fuera de esta decisión) |
| Lista concreta de reconocedores, filtros de falsos positivos y términos permitidos | ADR-013 (Fuera de esta decisión); ACO-022; ACO-023 |
| Nombre exacto de la etiqueta genérica de persona y catálogo de etiquetas (TIPO_ETIQUETA) y de `tipo_entidad` | ADR-013 (Fuera de esta decisión); Modelo E/R |
| Formatos de entrada del Sprint 1 (texto frente a PDF o imagen) | ACO-020; ACO-051 P1; Wireframes, pantalla 3 |
| Contenido y límites de los campos de texto libre `motivo` y `motivo_resolucion`: pueden contener datos identificativos y ninguna fuente fija validación, límite ni anonimización | Modelo E/R (SOLICITUD_DESBLOQUEO_CREDITO); Wireframes 8 y 9 |
| Claims y expiración del JWT | ADR-011 (Fuera de esta decisión) |
| Semántica de posicion_inicio y posicion_fin | Modelo E/R |
| Diseño definitivo del derecho al olvido y del registro de auditoría | Arquitectura §16 nº 3–4 |
