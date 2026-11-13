# 08 — PLAN

> Pieza del arnés de ACOMPAS. Es una capa derivada: no decide, no es fuente de verdad y se regenera, no se edita a mano. Ante cualquier conflicto prevalece la fuente oficial. Las versiones exactas de las fuentes constan en `docs/arnes/MANIFIESTO.md`.

## Objetivo y alcance

Orden de ejecución por ACO, dependencias y aceptación del sprint en curso (Sprint 1). La unidad mínima es el ACO. La Ficha ACO define el alcance y la aceptación. El Documento Operativo organiza el sprint, y **su matriz prevalece sobre las fichas** en responsable, revisión, estimación y dependencias.

## Qué no contiene

- El contenido íntegro de las fichas: el agente debe leer siempre la ficha de su ACO en `docs/aco/ACO-XXX.md`.
- La planificación de sprints posteriores, salvo la nota de bloques del Sprint 2.
- Cargas por persona, salvo lo que condiciona el orden.

## Fuentes

- **Normativas:** Plan de Proyecto (§4: S1 y su hito); Plan de Trabajo (§4, §6, §9, §10); Documento Operativo del Sprint 1 (§2, §6, §9, §10, §11, §12, §13, §14); Arquitectura del Sistema (§14, §16); ADR-013, ADR-014 y ADR-015, los que nombran el registro del Plan de Trabajo §9 y los criterios D-03 y D-06.
- **Derivadas:** Fichas ACO de docs/aco/: ACO-011 a ACO-033, ACO-051 y ACO-052.

## 1. Objetivo e hito del Sprint 1

- **Objetivo:** primera versión funcional, con conversación con Claude sobre un informe oncológico sintético, autenticación y anonimización básica. *(Plan de Proyecto §4)*
- **Hito, 9 de noviembre de 2026 (demo interna):** un usuario autorizado accede, usa la interfaz mínima, aporta un documento oncológico sintético, el sistema lo procesa con el flujo de anonimización previsto y obtiene una respuesta de Claude basada en el documento. Sin datos reales de pacientes. *(Documento Operativo §14)* El ensayo general fue el 6 de noviembre, y la demo se ejecutó el 9 desde un commit etiquetado.
- **Cierre del Sprint 1, 12 de noviembre de 2026** *(Documento Operativo §14)*: la demo se ejecutó y el sprint se cierra con la decisión conjunta #137 (opción A1). Los criterios D-01 a D-06 quedan cumplidos, con su evidencia en el acta #150. El criterio de ingeniería (D-07) queda **no cumplido**: la CI está verde y no hay secretos en Git, pero los tests E2E de ACO-033 no existen. El cierre con esa excepción lo autoriza la decisión #137 y no cambia el criterio oficial de la demo. ACO-033 pasa al Sprint 2 y ese criterio se traslada como criterio heredado.
- **Criterios de la demo** *(Documento Operativo §14; derivan del hito del Sprint 1)*. La demo se supera si se cumplen todos. Su verificación está en 09-TESTS §1.

| ID | Criterio | Qué debe ocurrir |
|---|---|---|
| D-01 | Reproducibilidad | Una persona nueva clona el repositorio, ejecuta `docker compose up -d --build` y obtiene en `/health` la respuesta `{"status":"ok"}`. |
| D-02 | Acceso | Un usuario de la lista blanca inicia sesión con 2FA vía Keycloak y uno no autorizado es rechazado. Las peticiones al API llevan un JWT validado. |
| D-03 | Documento sintético | Se sube desde la interfaz mínima y pasa por Presidio (Nivel 1) con etiquetado automático y los dos umbrales de ADR-013: el de hallazgo, por debajo del cual la detección se descarta como ruido, y el de documento, por debajo del cual el documento se retiene. Un documento con confianza baja se retiene y no se carga. Un documento ilegible (texto extraído vacío) no se procesa y se avisa al paciente con un motivo distinto del de baja confianza. |
| D-04 | No persistencia del original | Se verifica que el documento original no queda guardado; solo el resultado anonimizado. |
| D-05 | Conversación | Claude responde a partir del documento anonimizado, con el disclaimer visible y sin datos reales de pacientes en ningún punto. |
| D-06 | Calidad mínima | El conjunto de casos de prueba sintéticos (ACO-051/052) pasa en el flujo completo. Objetivo de detección: no se escapa ninguna entidad de las categorías que ADR-013 garantiza (nombres de personas, identificadores, teléfono, fax y correo electrónico, dirección y fecha de nacimiento), en los casos definidos. |
| D-07 | Ingeniería | CI verde, tests E2E (ACO-033) pasando, sin secretos en Git y todos los cambios integrados por PR revisada. **No cumplido en el cierre**: faltan los tests E2E de ACO-033, traspasado al Sprint 2. |

Quedan fuera de la demo: los Niveles 2 y 3, el RAG, el historial, el VPS, y el derecho al olvido y la auditoría completos. *(Documento Operativo §14; Arquitectura §14)* Los criterios de las demos siguientes se definen en cada Documento Operativo. *(Documento Operativo §14)*
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
| 033 | Tests E2E — **traspasado al Sprint 2** (#137): no llegó al Sprint 1; su estimación y dependencia están en la matriz del S2 (#142) | Miguel | Luis | 6–8 h | 032 |
| 051 | Datos sintéticos para demo | Luis | Miguel | 4–6 h | — |
| 052 | Casos de prueba | Luis | Miguel | 4–6 h | 030/032 |

ACO-007 («esqueleto del backend», FastAPI) se entregó en la PR #1 (merge `4f5e360`). No tiene ficha en `docs/aco/` porque es anterior a las fichas: la dependencia «013/007» del ACO-014 remite a ese trabajo, ya integrado en `main`, y no a un ACO pendiente del Sprint 1. *(Documento Operativo §6)*

## 3. Cadenas de dependencias y puntos de entrega

*(Documento Operativo §11)*

- Identidad: 011 → 012 → 013 → 014 → 015.
- Frontend/API: 016 → 017/018 → 019.
- Anonimización: 020 → 021 → 022 → 023 → 024 → 025 → 026.
- Conversación: 027 → 028/030; 029 → 030 → 031.
- E2E: 019 + 024 + 030 → 032 → 033.
- Demo: 051 + 052 alimentan la validación del flujo 032/033.
- **Puntos de entrega entre personas:** el cliente de API (019, Miguel) y la conversación (030, Luis) acuerdan el contrato de API antes de integrarse en 032. Lo mismo ocurre con la API de anonimización (024) y la conversación.

**Planificación semanal orientativa** *(Documento Operativo §9)*. Las semanas 1–2, del 15 al 28 de septiembre, se dedicaron a la base técnica; S3 a S6 recogen lo integrado en `main` y S7 y S8, lo que queda hasta la demo:

| Semana | Miguel | Luis |
|---|---|---|
| **S3** 29 sep–5 oct | ACO-020 y 021 | — |
| **S4** 6–12 oct | ADR-013, fichas ACO y arnés (documentación) | ACO-051 |
| **S5** 13–19 oct | ACO-011, 016 y 022 | ACO-027 y 029 |
| **S6** 20–27 oct | ACO-012 y 017 | ACO-030 |
| **S7** 28 oct–2 nov | ACO-013 (#90), 022 (#89) y 021 (#94), pendientes de merge; #85 (ADR-014 en el Plan de Trabajo y cierre de la cuestión 7 en la Arquitectura); ACO-014, 015, 018 y 023 | ACO-031 y revisión de las PR de Miguel |
| **S8** 3–9 nov | ACO-019, 024, 025, 026 y 032; ACO-028 si ADR-015; ensayo general el 6. **ACO-033 no llegó y pasa al Sprint 2 (#137)** | ACO-052, revisión de 019–033 y ensayo |

Checkpoint del 3 de noviembre: ACO-019 y ACO-024 integrados o en revisión; sin ellos no arranca ACO-032. Ensayo general el 6 de noviembre, con el mismo guion y la misma checklist que la demo, y congelación de `main` esa noche; la demo del 9 se ejecutó desde un commit etiquetado. **No hay recorte de alcance:** ACO-052 y ACO-026 se mantuvieron completos. La única flexibilidad era ACO-028, que depende de ADR-015 y no es criterio de demo. *(Documento Operativo §9)*

## 4. Alcance del Sprint 1

**Fuera de alcance del Sprint 1** *(Documento Operativo §12; Arquitectura §14)*: documentos reales de pacientes; anonimización de Niveles 2 y 3; RAG completo; VPS y despliegue de producción; persistencia e historial de conversaciones; derecho al olvido y auditoría completos (Sprint 2); cambios de alcance no aprobados.

**Traspaso al Sprint 2** *(Documento Operativo §6, §14)*: ACO-033 (tests E2E) no llegó al Sprint 1 y pasa al Sprint 2 con su criterio de demo como criterio heredado. Su estimación y dependencia se recogen en la matriz del S2 (#142).

**LLM gateway** *(Documento Operativo §13)*: ACO-027 fija el encaje mínimo que permite el flujo conversacional del Sprint 1, con el encaje arquitectónico definido y revisado por Miguel. **No debe convertirse en un desarrollo de plataforma completo.** El sprint de la implementación completa es provisional.

**Bloques del Sprint 2, por decidir en su planificación** *(Plan de Trabajo §6)*: ACO-035 a 046 (OCR, Niveles 2 y 3, métricas, modelo de datos definitivo, auditoría, borrado, prompt injection y límites del LLM) y ACO-053 a 056 (seguridad transversal, VPS, staging y demo ACANPAN). **No se implementan en el Sprint 1.**

## 5. Estado de las fichas y aceptación por ACO

La ficha es la fuente del alcance y de los criterios de aceptación *(Plan de Trabajo §4)*:

- **Ficha de alcance:** la de `docs/aco/ACO-XXX.md`, con objetivo, alcance y criterios de aceptación, sin responsable, estimación ni dependencias (están en la matriz de §2).
- **Ficha ejecutable:** la ficha de alcance ampliada con la plantilla `docs/aco/PLANTILLA.md`. El responsable del ACO la amplía al empezarlo, a mano o con un agente de IA, y la ampliación es el **primer commit de la PR** del ACO. El revisor revisa primero la ficha ampliada y después el código. Un agente no empieza BUILD sobre una ficha sin ampliar (`AGENTS.md`).

Estado de las fichas en el commit del manifiesto:

| Estado de la ficha | ACO |
|---|---|
| Ficha ejecutable con criterios confirmados en la revisión de su PR | 011, 012, 013, 014, 016, 017, 018, 019, 022, 023, 024, 025, 026, 027, 029, 030, 031, 051, 052 |
| Ficha revisada, con puntos confirmados y la ejecución de P9 y P10 anotada | 015 |
| Ficha ejecutable con criterios confirmados, pendiente de aprobación final | 028 |
| Ficha ejecutable (criterios AC-01…AC-09, tests, componentes y BLOQUEO), sin indicación expresa de estado | 021 |
| Ficha ampliada con criterios declarados **pendientes** en la propia ficha | 032. Su línea de estado la corrige #149, que está abierta |
| Ficha de alcance | 020, 033 |

Resumen de alcance de cada ACO *(fichas, §Objetivo, §Incluye y §Fuera de alcance; el texto completo está en cada ficha)*:

| ACO | Debe quedar hecho | Fuera de alcance |
|---|---|---|
| 011 | Keycloak ejecutable en local, reproducible y preparado para el realm | Realm y OIDC (012–013) |
| 012 | Realm reproducible, con configuración base para clientes y usuarios del piloto, `defaultRole` explícito y sin `offline_access` en el rol por defecto; configuración posterior a la importación con scripts; documentado | Flujo OIDC de la app (013) |
| 013 | Cliente y protocolo OIDC; login verificable en local; configuración documentada | JWT (014), whitelist (015) |
| 014 | El backend rechaza tokens ausentes o inválidos y acepta uno válido; pruebas de autorización | Redefinir Keycloak/OIDC |
| 015 | Acceso del usuario autorizado; rechazo del no autorizado con 403 genérico; lista en `EMAILS_AUTORIZADOS` (local/demo); sin correspondencia email↔UUID en ACOMPAS | Sustituir Keycloak; gestión completa de usuarios |
| 016 | React ejecutable en local con la estructura inicial | Layout y login (017–018) |
| 017 | Layout navegable para el login y la conversación, sin funciones fuera del Sprint 1 | Autenticación (018) |
| 018 | Login sobre `AuthShell` (sin cabecera, navegación, pie ni disclaimer) con el flujo configurado; resultado compatible con el backend; errores básicos; utilizable a 360 px sin scroll horizontal | Cliente de API (019); layout y `AuthShell` (017) |
| 019 | Cliente centralizado con autenticación; contrato documentado para 032 | API de anonimización (024) |
| 020 | Contrato de entrada y salida sobre texto, invocable desde Python, sin persistencia del original, con tests unitarios | Presidio, reconocedores, umbral, API HTTP |
| 021 | `AnalyzerEngine` en español con MEDDOCAN y puntuaciones; mapeo explícito | Reconocedores propios, política, umbral, anonimización, API, persistencia |
| 022 | Reconocedores específicos para identificadores clínicos españoles; cobertura de los identificadores del Sprint 1; asignación de rol por pistas de contexto y propagación entre las menciones del mismo nombre (R-53); separación detección/decisión | Umbral y política (023) |
| 023 | Umbral configurable y documentado; filtros de falsos positivos; separación detectado/anonimizado; no pasan documentos que no validen | API HTTP (024); persistencia; olvido |
| 024 | Endpoint interno documentado; texto → anonimizado según 020; errores; no devuelve el original | Persistencia del original (025) |
| 025 | Original fuera de la BD, del almacenamiento y de los logs; respuesta mínima; tests de ausencia de persistencia | Olvido y auditoría completos |
| 026 | Tests de detección, anonimización, umbral y falsos positivos, API y no persistencia, en CI | Niveles 2 y 3; cobertura de producción |
| 027 | Contrato mínimo entre conversación y proveedor; integración mínima con Claude; secretos compatibles con 028; encaje revisado | Plataforma completa; RAG |
| 028 | Clave por configuración segura del backend; fuera del código, de las respuestas HTTP y del navegador; pruebas o revisión | Gateway completo (027) |
| 029 | Prompt versionado: comprensión, no diagnóstico; restricciones de seguridad; control inicial de prompt injection | Flujo conversacional (030) |
| 030 | Consulta sobre el documento; contexto controlado; respuesta visible; sin documentos reales | Disclaimer (031); RAG |
| 031 | Disclaimer en el pie permanente de `AppShell`, slot `disclaimer` (el punto definido por UX); aclara que no sustituye al profesional; respuestas no presentadas como diagnóstico; legible a 360 px | Cambiar el contenido clínico, los controles técnicos, el layout o `AppShell` |
| 032 | Login → acceso autorizado → subida (pantalla 3) → anonimización → resultado de la validación (pantalla 4) → conversación → respuesta, todo dentro de `AppShell`; utilizable a 360 px; contratos integrados; ejecutable en local | Funciones de producción; datos reales; revisión manual de la pantalla 4 (S2); contenido del disclaimer (031) |
| 033 | E2E: caso feliz, usuario no autorizado y documento que no valida (si el flujo lo contempla); CI o dependencia documentada. **Traspasado al Sprint 2** (#137): no llegó al Sprint 1 | Sustituir los tests de 026 |
| 051 | Corpus sintético y manifiesto (ver 06-SEMILLA) | Ver ficha §5 |
| 052 | Casos de consulta, fuera de alcance, disclaimer y seguridad conversacional, preparados para la demo | Ampliar el alcance funcional |

**Política de anonimización del Nivel 1** (ADR-013, en el registro del Plan de Trabajo §9, que resuelve el umbral y el documento retenido de ACO-023): las reglas que aplican ACO-022, ACO-023 y ACO-026 están en 03-REGLAS (R-13, R-44…R-50, R-53), y sus verificaciones, en 09-TESTS. La propagación del rol entre menciones del mismo nombre la fija ADR-014; la gestión de la API key, ADR-015 (R-54).

**Criterio de revisión común de las fichas de alcance:** la persona revisora comprueba que el código implementa el objetivo de la ficha, que se respetan las dependencias, que hay pruebas cuando el comportamiento es verificable y que no se introducen datos reales, persistencia ni secretos fuera del alcance. *(Fichas ACO, §Criterio de revisión)*

## 6. Definition of Done

*(Plan de Trabajo §10; Documento Operativo §10)*

La Definition of Done es **única**: la del Plan de Trabajo §10. El Documento Operativo no la repite y añade un solo criterio propio del Sprint 1.

- Criterios de aceptación de la ficha cumplidos.
- Código implementado y revisado.
- Tests correspondientes ejecutados y CI verde.
- Documentación actualizada cuando corresponda.
- Sin secretos ni datos reales de pacientes.
- Integraciones afectadas comprobadas.
- PR enlazada a su ficha e Issue.
- *(Criterio propio del Sprint 1)* Funciona en Docker/local o deja documentada cualquier dependencia adicional.

## Cuestiones abiertas

| Cuestión | Fuente |
|---|---|
| Criterios de aceptación pendientes en la ficha de ACO-032: su línea de estado la corrige #149, que está abierta. | Ficha ACO-032; PR #149 |
| Lista concreta de reconocedores, filtros de falsos positivos y términos permitidos de ACO-022 y ACO-023: la fijan sus fichas al ampliarse. | ADR-013 (Fuera de esta decisión); ACO-022; ACO-023 |
| Encaje del gateway y modelo de Claude: cuestiones abiertas de la Arquitectura §16 nº 12–13, pendientes de ADR. | Arquitectura §16 nº 12–13 |
| ADR del entorno de desarrollo (decisión ya adoptada, ADR sin redactar). | Arquitectura §16 nº 11 |
| ACO-033 está traspasado al Sprint 2, pero el alcance del Sprint 2 no está decidido y su matriz depende de esa decisión (#142, #144). | Documento Operativo §6, §14; Plan de Trabajo §6 |
| Contenido y límites de los campos de texto libre `motivo` y `motivo_resolucion` de la solicitud de desbloqueo. | Modelo E/R (SOLICITUD_DESBLOQUEO_CREDITO); Wireframes 8 y 9 |
