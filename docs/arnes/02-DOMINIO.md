# 02 — DOMINIO

> Pieza del arnés de ACOMPAS. Es una capa derivada: no decide, no es fuente de verdad y se regenera, no se edita a mano. Ante cualquier conflicto prevalece la fuente oficial. Las versiones exactas de las fuentes constan en `docs/arnes/MANIFIESTO.md`.

## Objetivo y alcance

Conceptos del dominio, entidades, identificadores y relaciones. El agente lo usa para nombrar y modelar sin inventar.

## Qué no contiene

- Las reglas de tratamiento: están en 03-REGLAS.
- Los contratos de API: están en 07-INTERCAMBIO.
- El DDL ni las migraciones: el modelo relacional definitivo es una cuestión abierta.
- El diagrama E/R: consúltalo en el Modelo E/R.

## Fuentes

- **Normativas:** Plan de Proyecto (§1, §2); Arquitectura del Sistema (§1, §4, §6, §7, §8, §9); ADR-001, ADR-002, ADR-003, ADR-005, ADR-006, ADR-007, ADR-009, ADR-010, ADR-011 y ADR-012.
- **Derivadas:** Casos de Uso (§1–§3); Modelo E/R (§1 Visión general, §2 Definición de entidades —tipos y restricciones según el MANIFIESTO—, §3 Relaciones, §4 Notas de implementación).
- **Prevalencia (Estrategia §4.6):** el Modelo E/R aporta la estructura. En identificadores, identidad y límites técnicos prevalecen los ADR y la Arquitectura.

## 1. Conceptos

| Concepto | Definición | Fuente |
|---|---|---|
| Paciente | Usuario principal. En ACOMPAS se identifica solo por un UUID; nunca se almacena su email ni su identidad real. | ADR-001; Arquitectura §9 |
| Administrador | Cuenta interna: gestiona usuarios, roles, lista blanca y desbloqueos. | ADR-002; ADR-011 |
| Correspondencia email↔UUID | La custodia en exclusiva Keycloak. ACOMPAS no la guarda. | ADR-001 |
| Lista blanca (piloto) | Emails autorizados por ACANPAN antes del registro. Se guarda en la base de datos de ACOMPAS sin referencia al UUID del paciente. | ADR-009 |
| Documento original | Fichero clínico que sube el paciente. Se procesa en memoria o en un volumen efímero y no se persiste. | ADR-005 |
| Documento anonimizado | Resultado de la anonimización: es lo único que se guarda del documento. | ADR-005; Arquitectura §4 |
| Nombre genérico | Nombre del documento formado por el tipo de documento y la fecha de carga. Sustituye al nombre del fichero original. | ADR-012 |
| Hash del fichero | Hash criptográfico del fichero original, único por paciente, para detectar subidas repetidas. | ADR-012 |
| Etiqueta de anonimización | Reemplazo de una entidad identificativa, numerado **por documento** (`[MÉDICO_1]` en un documento no tiene relación con `[MÉDICO_1]` en otro). No guarda el valor original. | ADR-012; Arquitectura §4 |
| Niveles de anonimización | Nivel 1: Presidio, etiquetado y validación por umbral. Nivel 2: validación reforzada sobre texto de OCR local. Nivel 3: revisión manual y opcional del paciente sobre el resultado ya anonimizado. | ADR-003; Arquitectura §4 |
| Documento retenido | Documento cuya confianza de validación es baja: se retiene y no se carga. Su tratamiento posterior está abierto. | ADR-003; ver Cuestiones abiertas |
| LLM gateway | Módulo por el que pasa toda llamada a Claude API. Integra el control de gasto y el clasificador de intención. | ADR-006; Arquitectura §8 |
| Crédito | Tope diario y mensual por paciente, crédito acumulado con el sobrante diario, desbloqueo manual, modo pruebas, marca de susceptible de bloqueo y de crédito infinito. | Arquitectura §8 |
| Glosario (D6) | Se construye progresivamente con el LLM, sin semilla inicial validada. Cada entrada tiene un estado de validación. | Arquitectura §6 |
| Origen de la respuesta (D7) | Fuente recuperada (documento del paciente, glosario o RAG) o conocimiento interno del LLM, indicado con claridad. | Arquitectura §6 |
| Preferencia del resumen | Ocultar o Anotar un campo o sección del resumen clínico. Vive separada del resumen y se reaplica en cada generación. | Arquitectura §7 |

## 2. Identificadores

- **Paciente:** UUID asignado o resuelto por Keycloak. Es el único identificador del paciente en ACOMPAS. *(ADR-001; Arquitectura §9; Modelo E/R PACIENTE)*
- **Resto de entidades:** PK de tipo UUID en el Modelo E/R. *(Modelo E/R §2)* El «modelo de datos definitivo: UUID como identificador» sigue abierto *(Arquitectura §16 nº 5)*.
- **Etiquetas:** `numero` dentro de cada documento; no existe numeración global. *(ADR-012)*

## 3. Entidades

*(Modelo E/R §2. Se listan los atributos y las restricciones relevantes; las descripciones completas están en el Modelo E/R.)*

| Entidad | Atributos (tipo · restricción) | Notas con fuente |
|---|---|---|
| ADMINISTRADOR | administrador_id UUID PK · keycloak_id VARCHAR NN · nombre VARCHAR NN · email VARCHAR NN · activo BOOLEAN NN · creado_en TIMESTAMP NN | Única cuenta interna (ADR-002). |
| PACIENTE | paciente_id UUID PK (de Keycloak) · creado_en TIMESTAMP NN · activo BOOLEAN NN | Sin email ni datos personales (ADR-001). activo = false si se ha solicitado el derecho al olvido. |
| EMAIL_AUTORIZADO | email_autorizado_id UUID PK · email VARCHAR UNIQUE · autorizado_por VARCHAR · usado BOOLEAN · creado_en TIMESTAMP | Sin FK ni referencia al UUID (ADR-009). La comprobación es aplicativa, en el login (UC-03). |
| TIPO_DOCUMENTO | tipo_doc_id UUID PK · nombre VARCHAR NN · descripcion TEXT | Catálogo. |
| DOCUMENTO | documento_id UUID PK · paciente_id UUID FK · tipo_doc_id UUID FK · nombre VARCHAR NN (genérico) · ruta_almacen VARCHAR NN · hash_fichero VARCHAR NN · estado_anon VARCHAR NN · confianza_automatica DECIMAL (0–1) · validado_en TIMESTAMP · creado_en TIMESTAMP NN | ruta_almacen apunta al documento **anonimizado**; la tecnología de almacenamiento está abierta (ADR-005, ADR-010). Índice único (paciente_id, hash_fichero) (ADR-012). Valores de estado_anon según el Modelo E/R: `pendiente`, `validado`, `retenido_baja_confianza`. |
| TIPO_ETIQUETA | tipo_etiqueta_id UUID PK · etiqueta VARCHAR NN · descripcion TEXT | Catálogo de tipos sin numeración (ADR-012). |
| ETIQUETA_ANONIMIZACION | etiqueta_id UUID PK · documento_id UUID FK · tipo_etiqueta_id UUID FK · numero INTEGER NN · tipo_entidad VARCHAR NN · fuente VARCHAR NN · confirmada BOOLEAN NN · posicion_inicio INTEGER · posicion_fin INTEGER | Sin valor original (ADR-012). fuente ∈ {`presidio`, `paciente`} (ADR-003). La semántica de las posiciones está abierta. |
| SESION | sesion_id UUID PK · paciente_id UUID FK · titulo · tema · iniciada_en NN · ultima_actividad NN · activa NN | Varias conversaciones temáticas por paciente (S3). |
| MENSAJE | mensaje_id UUID PK · sesion_id UUID FK · rol VARCHAR NN (`usuario`/`asistente`) · contenido TEXT NN · tokens_usados INTEGER · fragmentos_rag UUID[] · creado_en NN | Índice (sesion_id, creado_en). |
| PUBLICACION | publicacion_id UUID PK · pmcid NN · titulo NN · autores · año · doi · tipo_evidencia · curada NN · activa NN · indexada_en NN · invalidada_en · motivo_invalidacion · referencia_curaduria | RAG (Fase 1.5). Índice parcial WHERE activa = true. |
| FRAGMENTO_RAG | fragmento_id UUID PK · publicacion_id UUID FK · contenido TEXT NN · embedding VECTOR NN · posicion INTEGER NN · creado_en NN | Índice HNSW. La dimensión (768 en el Modelo E/R) depende del modelo de embeddings, que está abierto. |
| AUDITORIA | auditoria_id UUID PK · actor_id UUID · actor_tipo VARCHAR (`paciente`/`administrador`/`sistema`) · paciente_id UUID FK · accion VARCHAR NN · entidad_afectada · entidad_id · ip_origen · resultado VARCHAR NN (`exito`/`error`) · detalle TEXT · creado_en NN (inmutable) | actor_id es polimórfico, sin FK estricta. El modelo de auditoría definitivo está abierto. |
| PREFERENCIA_RESUMEN | preferencia_id UUID PK · paciente_id UUID FK · tipo VARCHAR NN (`ocultar`/`anotar`) · campo_o_seccion NN · texto TEXT · alcance NN (por defecto `siempre`) · creado_en NN | Arquitectura §7. |
| CONSUMO_LLM | consumo_id UUID PK · paciente_id UUID FK · tokens_consumidos INTEGER NN · creado_en NN | Una fila por llamada a través del gateway (ADR-006). |
| CREDITO_PACIENTE | paciente_id UUID PK/FK (1:1) · tope_diario DECIMAL NN · tope_mensual DECIMAL NN · credito_acumulado DECIMAL NN · susceptible_bloqueo NN · credito_infinito NN · modo_pruebas NN · actualizado_en NN | Arquitectura §8. |
| SOLICITUD_DESBLOQUEO_CREDITO | solicitud_id UUID PK · paciente_id UUID FK · fecha_solicitud NN · estado NN (`pendiente`/`aprobada`/`denegada`) · administrador_id UUID FK · fecha_resolucion | Solo la resuelve un administrador. |
| ENTRADA_GLOSARIO | termino_id UUID PK · termino NN · definicion NN · fuente · estado_validacion NN · fecha_cambio_estado · creado_en NN | Entidad independiente. Estados: ver la nota de §5. |

NN = NOT NULL.

## 4. Relaciones

*(Modelo E/R §3)*

- PACIENTE 1:N DOCUMENTO, SESION, PREFERENCIA_RESUMEN, CONSUMO_LLM, SOLICITUD_DESBLOQUEO_CREDITO y AUDITORIA (como paciente afectado). PACIENTE 1:1 CREDITO_PACIENTE.
- DOCUMENTO 1:N ETIQUETA_ANONIMIZACION. TIPO_DOCUMENTO 1:N DOCUMENTO. TIPO_ETIQUETA 1:N ETIQUETA_ANONIMIZACION.
- SESION 1:N MENSAJE. MENSAJE N:M FRAGMENTO_RAG. PUBLICACION 1:N FRAGMENTO_RAG.
- ADMINISTRADOR 1:N SOLICITUD_DESBLOQUEO_CREDITO (resolución). AUDITORIA.actor_id es polimórfico.
- EMAIL_AUTORIZADO → PACIENTE: relación lógica, sin FK; el paciente solo se crea si su email está autorizado.

## 5. Discrepancias resueltas por prevalencia

| Tema | Fuente derivada | Fuente que prevalece | Aplicación en el arnés |
|---|---|---|---|
| Estados de ENTRADA_GLOSARIO | Modelo E/R: `pendiente_de_validacion`, `consolidada`, `corregida`, `descartada` | Arquitectura §6 y §9: pendiente, validada, corregida o descartada | Se usan los estados de la Arquitectura. El literal de los valores en BD queda pendiente de alinear (ver INFORME-GENERACION). Fuera del Sprint 1. |

## Cuestiones abiertas

| Cuestión | Fuente |
|---|---|
| Modelo de datos definitivo (UUID como identificador, ETIQUETA_ANONIMIZACION) | Arquitectura §16 nº 5; Plan de Trabajo §9 |
| posicion_inicio y posicion_fin: a qué texto se refieren, dado que el original no se conserva. Se decide antes de implementar el Nivel 3. | Modelo E/R (ETIQUETA_ANONIMIZACION) |
| Tratamiento del documento retenido por baja confianza: el Modelo E/R habla de «revisión posterior», UC-06 de que «lo revise el paciente», el wireframe 4 de que no se muestra, y el ADR sigue pendiente. | Plan de Trabajo §9; UC-06; Wireframes, pantalla 4; Modelo E/R (DOCUMENTO) |
| Almacenamiento del documento anonimizado (tecnología de ruta_almacen) | Arquitectura §16 nº 2; ADR-010 |
| Modelo del registro de auditoría: eventos e identificador | Arquitectura §16 nº 4 |
| Modelo de embeddings, dimensionalidad y chunking | ADR-007 (Fuera de esta decisión); Plan de Trabajo §9 |
| Agrupación de variantes de un nombre dentro de un documento; algoritmo del hash; formato exacto del nombre genérico | ADR-012 (Fuera de esta decisión) |
| Paciente con dos emails distintos en momentos diferentes | ADR-001 (Fuera de esta decisión) |
| Campo «motivo» de la solicitud de desbloqueo: aparece en el wireframe 8, pero no existe atributo en SOLICITUD_DESBLOQUEO_CREDITO | Wireframes, pantalla 8; Modelo E/R |
