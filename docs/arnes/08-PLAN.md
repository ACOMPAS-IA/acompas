# 08 — PLAN

> Pieza del arnés de ACOMPAS. Es una capa derivada: no decide, no es fuente de verdad y se regenera, no se edita a mano. Ante cualquier conflicto prevalece la fuente oficial. Las versiones exactas de las fuentes constan en `docs/arnes/MANIFIESTO.md`.

## Objetivo y alcance

Orden de ejecución por ACO, dependencias y aceptación del sprint en curso (Sprint 1). La unidad mínima es el ACO. La Ficha ACO define el alcance y la aceptación. El Documento Operativo organiza el sprint, y **su matriz prevalece sobre las fichas** en responsable, revisión, estimación y dependencias.

## Qué no contiene

- El contenido íntegro de las fichas: el agente debe leer siempre la ficha de su ACO en `docs/aco/ACO-XXX.md`.
- La planificación de sprints posteriores, salvo la nota de bloques del Sprint 2.
- Cargas por persona, salvo lo que condiciona el orden.

## Fuentes

- **Normativas:** Plan de Proyecto (§4: S1 y su hito); Plan de Trabajo (§4, §6, §10, §11); Documento Operativo del Sprint 1 (§2, §6, §9, §10, §11, §12, §13, §14).
- **Derivadas:** Fichas ACO de docs/aco/: ACO-011 a ACO-033, ACO-051 y ACO-052.

## 1. Objetivo e hito del Sprint 1

- **Objetivo:** primera versión funcional, con conversación con Claude sobre un informe oncológico sintético, autenticación y anonimización básica. *(Plan de Proyecto §4)*
- **Hito, 27 de octubre de 2026 (demo interna):** un usuario autorizado accede, usa la interfaz mínima, aporta un documento oncológico sintético, el sistema lo procesa con el flujo de anonimización previsto y obtiene una respuesta de Claude basada en el documento. Sin datos reales de pacientes. *(Documento Operativo §14)*
- **Criterios de la demo** *(Plan de Trabajo §11)*. La demo se supera si se cumplen todos. Su verificación está en 09-TESTS §1.

| ID | Criterio | Qué debe ocurrir |
|---|---|---|
| D-01 | Reproducibilidad | Una persona nueva clona el repositorio, ejecuta `docker compose up -d --build` y obtiene en `/health` la respuesta `{"status":"ok"}`. |
| D-02 | Acceso | Un usuario de la lista blanca inicia sesión con 2FA vía Keycloak y uno no autorizado es rechazado. Las peticiones al API llevan un JWT validado. |
| D-03 | Documento sintético | Se sube desde la interfaz mínima y pasa por Presidio (Nivel 1) con etiquetado automático y umbral de confianza. Un documento con confianza baja se retiene y no se carga. |
| D-04 | No persistencia del original | Se verifica que el documento original no queda guardado; solo el resultado anonimizado. |
| D-05 | Conversación | Claude responde a partir del documento anonimizado, con el disclaimer visible y sin datos reales de pacientes en ningún punto. |
| D-06 | Calidad mínima | El conjunto de casos de prueba sintéticos (ACO-051/052) pasa en el flujo completo. Objetivo de detección: no se escapa ninguna entidad de los casos definidos. |
| D-07 | Ingeniería | CI verde, tests E2E (ACO-033) pasando, sin secretos en Git y todos los cambios integrados por PR revisada. |

Quedan fuera de la demo: los Niveles 2 y 3, el RAG, el historial, el VPS, y el derecho al olvido y la auditoría completos. *(Plan de Trabajo §11)*
- **Situación de partida:** GitHub con flujo de PR, Docker/WSL2, PostgreSQL + pgvector local, FastAPI con `/health`, CI con pytest en GitHub Actions, sin VPS. *(Documento Operativo §2)*

## 2. Matriz operativa (fuente única de responsable, revisión, estimación y dependencias)

*(Documento Operativo §6)*

| ACO | Trabajo | Responsable | Soporte / revisión | Estimación | Dependencias |
|---|---|---|---|---|---|
| 011 | Keycloak local | Miguel | Luis | 3–4 h | — |
| 012 | Realm/configuración | Miguel | Luis | 3–4 h | 011 |
| 013 | OAuth2/OIDC | Miguel | Luis | 4–5 h | 012 |
| 014 | Validación JWT | Miguel | Luis | 4–5 h | 013/007 |
| 015 | Whitelist piloto | Miguel | Luis | 2–3 h | 012/013 |
| 016 | React bootstrap | Miguel | — | 3–4 h | — |
| 017 | Layout | Miguel | Luis | 3–4 h | 016 |
| 018 | Login | Miguel | Luis | 4–5 h | 013/016 |
| 019 | API client | Miguel | Luis | 4–5 h | 014/018 |
| 020 | Servicio anonimización | Miguel | Luis | 8–10 h | — |
| 021 | Presidio + MEDDOCAN | Miguel | Luis | 10–12 h | 020 |
| 022 | Etiquetado automático | Miguel | Luis | 6–8 h | 021 |
| 023 | Umbral de confianza | Miguel | Luis | 6–8 h | 022 |
| 024 | API anonimización | Miguel | Luis | 6–8 h | 020–023 |
| 025 | No persistencia del original | Miguel | Luis | 4–6 h | 024 |
| 026 | Tests anonimización | Miguel | Luis | 8–10 h | 021–025 |
| 027 | LLM Gateway v0 / encaje | Luis | Miguel (define el encaje y revisa) | 6–8 h | — |
| 028 | Seguridad de API key | Miguel | Luis | 3–4 h | 027 |
| 029 | System prompt v0 | Luis | Miguel (revisa seguridad) | 5–6 h | — |
| 030 | Conversación sobre documento | Luis | Miguel | 8–10 h | 027/029 |
| 031 | Disclaimer | Luis | Miguel | 2–3 h | 030 |
| 032 | Flujo E2E | Miguel | Luis | 8–10 h | 019/024/030 |
| 033 | Tests E2E | Miguel | Luis | 6–8 h | 032 |
| 051 | Datos sintéticos para demo | Luis | Miguel | 4–6 h | — |
| 052 | Casos de prueba | Luis | Miguel | 4–6 h | 030/032 |

## 3. Cadenas de dependencias y puntos de entrega

*(Documento Operativo §11)*

- Identidad: 011 → 012 → 013 → 014 → 015.
- Frontend/API: 016 → 017/018 → 019.
- Anonimización: 020 → 021 → 022 → 023 → 024 → 025 → 026.
- Conversación: 027 → 028/030; 029 → 030 → 031.
- E2E: 019 + 024 + 030 → 032 → 033.
- Demo: 051 + 052 alimentan la validación del flujo 032/033.
- **Puntos de entrega entre personas:** el cliente de API (019, Miguel) y la conversación (030, Luis) acuerdan el contrato de API antes de integrarse en 032. Lo mismo ocurre con la API de anonimización (024) y la conversación.

**Planificación semanal orientativa** *(Documento Operativo §9)*: S3 (29 sep–5 oct) 020, 011, 012, 016, 017 · 027 e inicio de 029. S4 (6–12 oct) 021, 013, 014, 015, 018, 028 · fin de 029 y 051. S5 (13–19 oct) 022, 023, 024, 019 y la primera mitad de 026 · 030. S6 (20–27 oct) 025, segunda mitad de 026, 032, 033 · 031, 052 e integración. **Si hay desviación, el primer recorte es ACO-052, y después se aplaza a S6 parte de ACO-026.**

## 4. Alcance del Sprint 1

**Fuera de alcance del Sprint 1** *(Documento Operativo §12; Plan de Trabajo §11)*: documentos reales de pacientes; anonimización de Niveles 2 y 3; RAG completo; VPS y despliegue de producción; persistencia e historial de conversaciones; derecho al olvido y auditoría completos (Sprint 2); cambios de alcance no aprobados.

**LLM gateway** *(Documento Operativo §13)*: ACO-027 fija el encaje mínimo que permite el flujo conversacional del Sprint 1, con el encaje arquitectónico definido y revisado por Miguel. **No debe convertirse en un desarrollo de plataforma completo.** El sprint de la implementación completa es provisional.

**Bloques del Sprint 2, por decidir en su planificación** *(Plan de Trabajo §6)*: ACO-035 a 046 (OCR, Niveles 2 y 3, métricas, modelo de datos definitivo, auditoría, borrado, prompt injection y límites del LLM) y ACO-053 a 056 (seguridad transversal, VPS, staging y demo ACANPAN). **No se implementan en el Sprint 1.**

## 5. Estado de las fichas y aceptación por ACO

La ficha es la fuente del alcance y de los criterios de aceptación *(Plan de Trabajo §4)*. Estado de las fichas en el commit del manifiesto:

| Estado de la ficha | ACO |
|---|---|
| Ficha ejecutable con criterios confirmados en la revisión de su PR | 051 |
| Ficha ejecutable (criterios AC-01…AC-09, tests, componentes y BLOQUEO), sin indicación expresa de estado | 021 |
| Ficha de alcance (objetivo, incluye, fuera de alcance y criterio de revisión), con criterios **pendientes de revisión** por Miguel y Luis | 027, 029, 030, 031, 052 |
| Ficha de alcance | 011–020, 022–026, 028, 032, 033 |

Resumen de alcance de cada ACO *(fichas, §Objetivo, §Incluye y §Fuera de alcance; el texto completo está en cada ficha)*:

| ACO | Debe quedar hecho | Fuera de alcance |
|---|---|---|
| 011 | Keycloak ejecutable en local, reproducible y preparado para el realm | Realm y OIDC (012–013) |
| 012 | Realm reproducible, con configuración base para clientes y usuarios del piloto, documentado | Flujo OIDC de la app (013) |
| 013 | Cliente y protocolo OIDC; login verificable en local; configuración documentada | JWT (014), whitelist (015) |
| 014 | El backend rechaza tokens ausentes o inválidos y acepta uno válido; pruebas de autorización | Redefinir Keycloak/OIDC |
| 015 | Acceso del usuario autorizado; rechazo del no autorizado; sin correspondencia email↔UUID en ACOMPAS | Sustituir Keycloak; gestión completa de usuarios |
| 016 | React ejecutable en local con la estructura inicial | Layout y login (017–018) |
| 017 | Layout navegable para el login y la conversación, sin funciones fuera del Sprint 1 | Autenticación (018) |
| 018 | Login con el flujo configurado; resultado compatible con el backend; errores básicos | Cliente de API (019) |
| 019 | Cliente centralizado con autenticación; contrato documentado para 032 | API de anonimización (024) |
| 020 | Contrato de entrada y salida sobre texto, invocable desde Python, sin persistencia del original, con tests unitarios | Presidio, reconocedores, umbral, API HTTP |
| 021 | `AnalyzerEngine` en español con MEDDOCAN y puntuaciones; mapeo explícito | Reconocedores propios, política, umbral, anonimización, API, persistencia |
| 022 | Reconocedores específicos para identificadores clínicos españoles; cobertura de los identificadores del Sprint 1; separación detección/decisión | Umbral y política (023) |
| 023 | Umbral configurable y documentado; filtros de falsos positivos; separación detectado/anonimizado; no pasan documentos que no validen | API HTTP (024); persistencia; olvido |
| 024 | Endpoint interno documentado; texto → anonimizado según 020; errores; no devuelve el original | Persistencia del original (025) |
| 025 | Original fuera de la BD, del almacenamiento y de los logs; respuesta mínima; tests de ausencia de persistencia | Olvido y auditoría completos |
| 026 | Tests de detección, anonimización, umbral y falsos positivos, API y no persistencia, en CI | Niveles 2 y 3; cobertura de producción |
| 027 | Contrato mínimo entre conversación y proveedor; integración mínima con Claude; secretos compatibles con 028; encaje revisado | Plataforma completa; RAG |
| 028 | Clave por configuración segura del backend; fuera del código, de las respuestas HTTP y del navegador; pruebas o revisión | Gateway completo (027) |
| 029 | Prompt versionado: comprensión, no diagnóstico; restricciones de seguridad; control inicial de prompt injection | Flujo conversacional (030) |
| 030 | Consulta sobre el documento; contexto controlado; respuesta visible; sin documentos reales | Disclaimer (031); RAG |
| 031 | Disclaimer visible donde lo defina UX; aclara que no sustituye al profesional; respuestas no presentadas como diagnóstico | Cambiar el contenido clínico o los controles técnicos |
| 032 | Login → acceso autorizado → documento sintético → anonimización → conversación → respuesta; contratos integrados; ejecutable en local | Funciones de producción; datos reales |
| 033 | E2E: caso feliz, usuario no autorizado y documento que no valida (si el flujo lo contempla); CI o dependencia documentada | Sustituir los tests de 026 |
| 051 | Corpus sintético y manifiesto (ver 06-SEMILLA) | Ver ficha §5 |
| 052 | Casos de consulta, fuera de alcance, disclaimer y seguridad conversacional, preparados para la demo | Ampliar el alcance funcional |

**Criterio de revisión común de las fichas de alcance:** la persona revisora comprueba que el código implementa el objetivo de la ficha, que se respetan las dependencias, que hay pruebas cuando el comportamiento es verificable y que no se introducen datos reales, persistencia ni secretos fuera del alcance. *(Fichas ACO, §Criterio de revisión)*

## 6. Definition of Done

*(Plan de Trabajo §10; Documento Operativo §10. Se recoge la unión de las dos listas, que no se contradicen.)*

- Criterios de aceptación de la ficha cumplidos.
- Trabajo en una rama feature asociada al ACO; PR abierta, enlazada a su ficha y a su Issue.
- Código revisado por la otra persona y CI verde.
- Tests añadidos y ejecutados cuando el comportamiento es verificable.
- Sin secretos ni datos reales de pacientes.
- Funciona en Docker/local o deja documentada cualquier dependencia adicional.
- Revisión adecuada de seguridad, privacidad, autenticación e integración; integraciones afectadas comprobadas.
- Documentación actualizada cuando corresponda.

## Cuestiones abiertas

| Cuestión | Fuente |
|---|---|
| ACO-014 depende de «007» en la matriz, pero en docs/aco/ no hay ficha de ACO-007 (es anterior al Sprint 1). Qué entrega debe darse por cumplida no está documentado. | Documento Operativo §6; docs/aco/ |
| Criterios de aceptación de ACO-027, 029, 030, 031 y 052 pendientes de revisión: hasta que se confirmen, el alcance ejecutable es el de la ficha de alcance. | Fichas ACO-027, 029, 030, 031, 052 |
| Cómo pasa una ficha de alcance a ficha ejecutable (sección 0 de puntos a confirmar, aclaraciones) no lo describe el Plan de Trabajo; ACO-051 lo muestra con «criterios propuestos por el responsable, confirmados en la revisión de la PR». | Plan de Trabajo §4; ACO-051 |
| «Identificadores definidos para Sprint 1» (ACO-022) y «filtros para falsos positivos previstos» (ACO-023): no están enumerados en ninguna fuente. | ACO-022; ACO-023 |
| Umbral de confianza, tratamiento del documento retenido, gestión de secretos, encaje del gateway y modelo de Claude: ADR pendientes del Sprint 1. | Plan de Trabajo §9 |
| ADR del entorno de desarrollo (decisión ya adoptada, ADR sin redactar). | Plan de Trabajo §9 |
