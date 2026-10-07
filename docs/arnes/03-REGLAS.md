# 03 — REGLAS

> Pieza del arnés de ACOMPAS. Es una capa derivada: no decide, no es fuente de verdad y se regenera, no se edita a mano. Ante cualquier conflicto prevalece la fuente oficial. Las versiones exactas de las fuentes constan en `docs/arnes/MANIFIESTO.md`.

## Objetivo y alcance

Reglas de negocio, privacidad, seguridad, arquitectura y proceso que debe cumplir cualquier ACO. Cada regla lleva un identificador `R-NN`, su fuente y la verificación correspondiente de 09-TESTS (`T-NN`).

## Qué no contiene

- El comportamiento transversal del agente (jerarquía, bloqueo, fases): está en `AGENTS.md`.
- Las cuestiones abiertas convertidas en reglas: siguen abiertas al final de esta pieza.
- Las reglas propias de funcionalidades posteriores al Sprint 1 se incluyen solo cuando un ACO del Sprint 1 podría contradecirlas. En ese caso se marcan con *(posterior a S1)*.

## Fuentes

- **Normativas:** ADR-001 a ADR-012; Arquitectura del Sistema (§2, §3, §4, §5, §6, §8, §9, §10, §11, §13, §14, §15); Plan de Proyecto (§1, §2); Plan de Trabajo (§2, §4, §5, §8, §9, §10).
- **Derivadas:** Casos de Uso (UC-05, UC-07, UC-09); Fichas ACO de docs/aco/ (restricciones, criterios y BLOQUEO de ACO-014, 015, 021, 022, 023, 024, 025, 028, 031 y 051).
- **Prevalencia:** las fuentes oficiales prevalecen sobre las derivadas. Una Ficha ACO o el arnés nunca cambian una decisión del Plan de Proyecto, de la Arquitectura del Sistema ni de un ADR aprobado. *(Plan de Trabajo §4, Ejecución con agente)* El orden completo de precedencia está en `AGENTS.md`.

## 1. Privacidad y datos de pacientes

| ID | Regla | Fuente | Verificación |
|---|---|---|---|
| R-01 | No se usa ningún dato real de paciente en ningún entorno (desarrollo, pruebas ni producción) hasta que estén operativos la anonimización, el derecho al olvido básico y el registro de auditoría. En el Sprint 1 no se usan documentos reales. | ADR-008; Arquitectura §11, §13; Plan de Trabajo §2 | T-01 |
| R-02 | Las pruebas, fixtures y demos usan datos sintéticos. Ningún dato sintético puede tomarse ni adaptarse de un documento real. | Plan de Trabajo §10; ACO-051 §8, §10 | T-02 |
| R-03 | El documento original no se persiste: se procesa en memoria o en un volumen efímero, y solo se guarda el resultado anonimizado. | ADR-005; Arquitectura §4, §9; Plan de Trabajo §10 | T-03 |
| R-04 | El contenido de un documento clínico original no aparece en logs, mensajes de error, fixtures de prueba, commits, documentación, capturas ni ficheros temporales persistentes. | Arquitectura §11 (Protección de datos) | T-04 |
| R-05 | Las reglas de privacidad verificables se comprueban con tests automatizados cuando resulte razonable. | Arquitectura §11 | T-01…T-08 |
| R-06 | No se guarda el valor original de ninguna entidad detectada, ni cifrado ni de ninguna otra forma. | ADR-012 | T-05 |
| R-07 | No se conserva el nombre del fichero original: el documento lleva un nombre genérico (tipo de documento + fecha de carga). | ADR-012; Arquitectura §9 | T-06 |
| R-08 | Las etiquetas de anonimización se numeran por documento, sin coherencia entre documentos. | ADR-012; Arquitectura §4 | T-07 |
| R-09 | Se guarda un hash criptográfico del fichero original, único por paciente (no global). Ante un duplicado se avisa al paciente en lugar de reprocesarlo; si el paciente borró antes el documento, puede volver a subirlo. *(Posterior a S1: no hay persistencia de documentos en el Sprint 1.)* | ADR-012 | T-22 |
| R-10 | ACOMPAS identifica al paciente solo por UUID y nunca almacena su email. La correspondencia email↔UUID la custodia en exclusiva Keycloak. | ADR-001; Arquitectura §9, §11 | T-08 |
| R-11 | Cifrado en reposo (PostgreSQL y almacenamiento de objetos, si aplica) y en tránsito (TLS 1.2+). | Arquitectura §11, §13 | T-23 (revisión) |

## 2. Anonimización

| ID | Regla | Fuente | Verificación |
|---|---|---|---|
| R-12 | Ningún documento entra en el sistema sin pasar por el módulo de anonimización. | Arquitectura §2, §4; Plan de Proyecto §1 | T-09 |
| R-13 | La validación es automática, por umbral de confianza. Si la confianza es baja, el documento se retiene y no se carga ni pasa al flujo posterior. El valor del umbral y el tratamiento del documento retenido están abiertos (ver Cuestiones abiertas). | ADR-003; Arquitectura §4; ACO-023 | T-10 |
| R-14 | Claude API no interviene en la detección ni en la sustitución de entidades. El Nivel 3 es la revisión manual del paciente, no una segunda pasada del modelo. | ADR-003; UC-05 | T-11 |
| R-15 | En el Sprint 1 solo se implementa el Nivel 1 (Presidio, etiquetado automático y validación por umbral). Los Niveles 2 y 3 son del Sprint 2. | Arquitectura §4, §14 | T-24 (revisión) |
| R-16 | El OCR es exclusivamente local (Tesseract; docTR o PaddleOCR como alternativa). Ningún documento sale del servidor propio. *(Posterior a S1.)* | ADR-004 | T-24 (revisión) |
| R-17 | Se mantiene separado lo que se detecta de lo que se decide anonimizar. La detección (ACO-021, ACO-022) no fija la política ni el umbral (ACO-023). | ACO-021 §5, §8, §9; ACO-022; ACO-023 | T-12 |
| R-18 | La API de anonimización no devuelve el texto original en su respuesta. | ACO-024; ACO-025 | T-13 |

## 3. Identidad y acceso

| ID | Regla | Fuente | Verificación |
|---|---|---|---|
| R-19 | Keycloak self-hosted es el proveedor de identidad (OpenID Connect sobre OAuth 2.0). El 2FA es obligatorio para todos los usuarios. No se implementa un sistema de autenticación paralelo ni se guardan credenciales en la base de datos de ACOMPAS. | ADR-011; Arquitectura §11 | T-14 |
| R-20 | Las peticiones al backend llevan un JWT firmado y con expiración. El backend lo valida y aplica la autorización: rechaza los tokens ausentes o inválidos. | ADR-011; Arquitectura §3, §11; ACO-014 | T-15 |
| R-21 | Roles: paciente y administrador. Un paciente solo accede a sus recursos. | ADR-002; ADR-011 | T-16 |
| R-22 | Durante el piloto, solo pueden darse de alta los emails de la lista blanca autorizada por ACANPAN. La lista se guarda en la base de datos de ACOMPAS, la gestiona manualmente el administrador y no enlaza con el UUID. Keycloak solo resuelve o crea el UUID de un email autorizado. La lista blanca no sustituye a la autenticación. | ADR-009; ADR-001; Arquitectura §11; ACO-015 | T-17 |

## 4. Modelo de lenguaje y conversación

| ID | Regla | Fuente | Verificación |
|---|---|---|---|
| R-23 | Toda llamada a Claude API pasa por el LLM gateway. Ningún módulo llama a Claude API directamente. | ADR-006; Arquitectura §8 | T-18 |
| R-24 | Los secretos y credenciales nunca se almacenan en Git. La API key del proveedor LLM no aparece en el código fuente, en las respuestas HTTP, en los logs ni en el navegador. | Plan de Trabajo §10; ACO-028 | T-19 |
| R-25 | Prompt de sistema restringido al ámbito oncológico: el modelo declina educadamente las preguntas fuera de ese ámbito. | Arquitectura §3, §11 | T-20 |
| R-26 | Control de prompt injection: el prompt de sistema se estructura para rechazar instrucciones incrustadas en los documentos o en las preguntas, separando las instrucciones del sistema del contenido del usuario. | Arquitectura §11, §15 | T-20 |
| R-27 | Disclaimer permanente en la interfaz y en las respuestas: ACOMPAS no diagnostica ni sustituye al médico. | Arquitectura §11; Plan de Proyecto §1–2; ACO-031 | T-21 |
| R-28 | La respuesta indica su origen: la fuente recuperada en que se basa o, si no la hay, que procede del conocimiento interno del LLM (D7). Esta vía no amplía el ámbito permitido. | Arquitectura §6, §11; UC-09 | T-20 |
| R-29 | Control de gasto en el gateway: tope diario y mensual, crédito acumulado, uso del crédito con aviso, desbloqueo solo manual del administrador, modo pruebas (contabiliza sin bloquear, con crédito infinito) y marcas individuales. *(Posterior a S1: no lo exige ninguna ficha del Sprint 1.)* | Arquitectura §8; ADR-006 | T-25 (revisión) |

## 5. Arquitectura y tecnología

| ID | Regla | Fuente | Verificación |
|---|---|---|---|
| R-30 | Una sola base de datos de aplicación: PostgreSQL con pgvector, SQLAlchemy como capa de acceso y Alembic para migraciones. Añadir otra base de datos o un motor vectorial requiere una decisión explícita (ADR). | ADR-007; Arquitectura §10 | T-26 (revisión) |
| R-31 | No se usa MinIO para ningún almacenamiento. El almacenamiento de objetos está pendiente de decisión. | ADR-010 | T-26 (revisión) |
| R-32 | Stack aprobado: Python + FastAPI, React, Keycloak, Microsoft Presidio, Claude API, LlamaIndex, sentence-transformers locales y Tesseract. No se introducen Kubernetes, microservicios, colas ni almacenamiento S3 sin una necesidad demostrada y un ADR. | Arquitectura §10; Plan de Trabajo §2, §5, §8 | T-26 (revisión) |
| R-33 | Docker Compose es el entorno común; nadie depende del VPS para desarrollar. | Plan de Trabajo §5; Arquitectura §13 | T-27 |
| R-34 | Los embeddings se generan localmente: ningún contenido del paciente sale del servidor para vectorizarse. *(Posterior a S1.)* | Arquitectura §5, §11 | T-26 (revisión) |

## 6. Proceso de trabajo

| ID | Regla | Fuente | Verificación |
|---|---|---|---|
| R-35 | Ningún cambio directo sobre main. Flujo: Issue → rama → desarrollo local → tests → PR → revisión de la otra persona → CI verde → merge. | Plan de Trabajo §2, §4; Arquitectura §13 | T-28 |
| R-36 | Ramas `feature/ACO-XXX-descripcion` y `fix/ACO-XXX-descripcion`. La PR enlaza su ficha y su Issue; la Issue es solo un puntero. | Plan de Trabajo §4, §10 | T-28 |
| R-37 | Merge siempre squash, con título «ID: título» y cuerpo breve. Si ha intervenido un agente de IA, el commit final lleva una sola línea Co-Authored-By. El revisor aprueba o rechaza sin modificar el contenido y hace el merge, salvo que el autor pida esperar. | Plan de Trabajo §4 | T-28 |
| R-38 | Requieren decisión conjunta (Issue «decisión conjunta» con 48 h para objetar): mover ACOs entre sprints, nuevas dependencias, componentes o cambios de stack, cambios de seguridad o privacidad, cambios de contratos de API entre áreas, reasignaciones, reestimaciones de más del 50%, cambios que afecten a lo acordado con ACANPAN y las cuestiones abiertas de arquitectura. | Plan de Trabajo §8 | T-29 (revisión) |
| R-39 | Puede decidirlo la persona responsable, informando en la PR: refactors internos del ACO, corrección de bugs, ampliación de tests y documentación, dividir un ACO en Issues sin cambiar su alcance y ajustes menores de estimación. | Plan de Trabajo §8 | T-29 (revisión) |
| R-40 | Hace falta un ADR cuando la decisión es difícil de revertir, afecta a la seguridad, la privacidad o los datos de pacientes, cambia el stack, afecta a más de un área o se aparta del Plan o de la Arquitectura. Un ADR aprobado no se edita: se sustituye. | Plan de Trabajo §9 | T-29 (revisión) |
| R-41 | Las APIs se documentan antes de integrar frontend y backend. Los cambios en los contratos de API entre áreas requieren decisión conjunta. Los puntos de entrega del Sprint 1 están en 08-PLAN. | Plan de Trabajo §8, §10 | T-30 |
| R-42 | Las funciones críticas tienen tests antes de darse por terminadas, y la CI está verde antes del merge. | Plan de Trabajo §10 | T-28 |
| R-43 | No se desactivan controles de seguridad para facilitar una prueba. | Plan de Trabajo §4 (Ejecución con agente) | T-29 (revisión) |

## 7. Derecho al olvido y auditoría (posterior a S1)

Están previstos para el Sprint 2 *(Arquitectura §11, §14)*, y ningún ACO del Sprint 1 debe impedirlos:

- El borrado es completo y verificable para todos los datos asociados a un UUID, incluida la cuenta en Keycloak (Admin API). *(ADR-001; Arquitectura §11; UC-07)*
- El hash del fichero se borra con el documento (ADR-012). La secuencia de borrado de referencia del modelo de datos está en 02-DOMINIO y 07-INTERCAMBIO; el diseño definitivo está abierto.
- Registro de auditoría de accesos y operaciones sensibles (carga de documentos, borrados, accesos al historial). *(Arquitectura §11)*

## Cuestiones abiertas (no son reglas)

| Cuestión | Fuente |
|---|---|
| Valor del umbral de confianza (los wireframes muestran 0,85, pero no está decidido) y tratamiento del documento retenido. UC-06 dice que «lo revisa el paciente», el wireframe 4 que no se muestra y el Modelo E/R que se retiene «para revisión posterior». | Plan de Trabajo §9; ACO-023; ADR-003 (Fuera de esta decisión); UC-06; Wireframes, pantalla 4; Modelo E/R |
| Objetivo de cobertura de Presidio y reglas concretas. Más del 85% es objetivo de los Niveles 1–2, no criterio del Sprint 1. | ADR-003 (Fuera de esta decisión); Arquitectura §4 |
| Gestión de secretos y de la API key de Claude (ADR pendiente). | Plan de Trabajo §9; ACO-028 |
| Encaje mínimo y alcance del LLM gateway en el Sprint 1. | Plan de Trabajo §8, §9; Documento Operativo §13; ACO-027 |
| Modelo de Claude a usar y política de versiones. | Plan de Trabajo §9 |
| Sprint del clasificador de intención. | Arquitectura §16 nº 1; Plan de Trabajo §8, §9 |
| Diseño del derecho al olvido y modelo del registro de auditoría. | Arquitectura §16 nº 3–4 |
| Valores de expiración y claims del JWT, flujo OIDC concreto, política de contraseñas y recuperación. | ADR-011 (Fuera de esta decisión) |
| Cómo se comprueba la lista blanca y cómo se conecta con el login de Keycloak. | ADR-009 (Fuera de esta decisión) |
| Regla de cálculo del crédito y de los topes. | Plan de Trabajo §9 |
| Tono del LLM (D9). | Plan de Proyecto §1 |
