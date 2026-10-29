# ADR-015 — Gestión de secretos y API key de Claude

Estado: propuesto

Sustituido por: —

Origen: Decisión conjunta #82 (acta de cierre de 28/10/2026), que recoge las precisiones aceptadas en los comentarios de 26/10/2026; ADR pendiente del Plan de Trabajo §9 (gestión de secretos y API key de Claude, ACO-028)

Relacionados: ADR-006, ADR-008

## Contexto

ACO-027 dejó implementado el mínimo para llamar a Claude API: `ANTHROPIC_API_KEY` como variable de entorno, leída solo en `get_api_key()`, guardada como `SecretStr`, con `.env` ignorado por Git y sin referencias en el frontend. Sus tests comprueban que la clave no aparece en logs ni en errores.

El Plan de Trabajo §9 tiene pendiente el ADR de gestión de secretos y API key de Claude, que ACO-028 necesita antes de implementar y verificar los controles. Es una decisión de seguridad y, por tanto, una decisión conjunta.

En la revisión de ACO-027 quedaron dos hallazgos (issue #33): con el logger raíz en DEBUG, el SDK `anthropic` puede registrar el cuerpo de las peticiones; y el SDK también lee variables de entorno distintas de la clave. Al contrastar el comportamiento con `anthropic` 1.17.0 —el rango del proyecto es `>=1.15,<2.0`— aparecen dos más:

- `ANTHROPIC_CUSTOM_HEADERS` añade cabeceras arbitrarias a todas las peticiones y se sigue aplicando aunque el cliente reciba `api_key`, `base_url` y `default_headers` explícitos. Verificado en el código de la versión 1.17.0: [anthropic-sdk-python v1.17.0, `_client.py`](https://github.com/anthropics/anthropic-sdk-python/blob/v1.17.0/src/anthropic/_client.py).
- las trazas OpenTelemetry del SDK están activadas por defecto en modo `metadata_only`, y con `ANTHROPIC_OPEN_TELEMETRY_TRACES_CONTENT_MODE=content` incluyen el contenido de peticiones y respuestas, es decir, el texto clínico. Hoy no se exporta nada porque no hay proveedor de trazas configurado, pero basta con instalar uno.

El cliente `httpx2` usa `trust_env=True` por defecto y respeta `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`, `SSL_CERT_FILE` y `SSL_CERT_DIR` del entorno; `trust_env=False` desactiva su uso ([documentación de variables de entorno de HTTPX2](https://pydantic.dev/docs/httpx2/api/environment_variables/)). Por eso, fijar `base_url` y rechazar las variables `ANTHROPIC_*` no basta para impedir que la conexión dependa del entorno.

La demo interna del 27/10/2026 se hizo con una clave personal. La clave del proyecto todavía no existe y su titularidad depende de ACANPAN o de la organización.

## Decisión

1. **Mecanismo en local y demo.** `ANTHROPIC_API_KEY` se inyecta solo en el servicio `backend` desde un `.env` local no versionado. En Linux/WSL2 el fichero tiene permisos 600. No se copia a la imagen y Compose solo pasa la variable al servicio `backend`. `.env.example` recoge los nombres de las variables de Claude con valores vacíos. Docker secrets y los gestores externos quedan para producción (punto 6).

2. **Titularidad de la clave.** Las claves personales son solo para desarrollo. La demo usa una clave del proyecto, de una cuenta de ACANPAN o de la organización, con titular, acceso a la consola y límite de gasto definidos. La demo interna del 27/10/2026 se hizo con una clave personal como excepción acotada: se rota después de la demo y se sustituye por la clave del proyecto en cuanto ACANPAN o la organización designen titular. La rotación y el incidente dependen de ese titular (punto 7).

3. **Variables que puede leer el SDK.** El proveedor construye el cliente con `api_key`, `base_url` explícito en el endpoint oficial, `open_telemetry=False` y `http_client=anthropic.DefaultHttpxClient(trust_env=False)`. Así se conservan los valores por defecto del SDK para `limits`, `timeout` y `follow_redirects`, y se desactivan los proxies y certificados del entorno. El `timeout` y `max_retries` siguen pasándose a `Anthropic`.

   Además, `load_settings()` rechaza cualquier variable de entorno cuyo nombre empiece por `ANTHROPIC_` salvo `ANTHROPIC_API_KEY`: lanza `not_configured` y registra solo el nombre de la variable, nunca su valor. La comprobación cubre, entre otras, `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_CUSTOM_HEADERS`, `ANTHROPIC_OPEN_TELEMETRY*`, `ANTHROPIC_LOG`, `ANTHROPIC_WEBHOOK_SIGNING_KEY` y `ANTHROPIC_PROFILE`. No se llama al proveedor. La aplicación arranca, `/health` responde y el gateway falla con `not_configured`, como en ACO-027. Se prefiere una lista de permitidas a una de prohibidas porque el rango `<2.0` puede añadir variables nuevas.

   Los tests comprueban el rechazo con una variable de cada familia y, con entorno limpio, verifican la URL y la cabecera de autenticación con `httpx2.MockTransport`. También comprueban que el cliente tiene `trust_env=False` y que señuelos en `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`, `SSL_CERT_FILE` y `SSL_CERT_DIR` no alteran la petición. Como `MockTransport` sustituye al transporte, la desactivación de proxies se verifica por `trust_env=False`; el test no simula un proxy real.

4. **Registro del SDK.** Al arrancar, la aplicación configura el registro y comprueba que los loggers del SDK que puedan emitir contenido —`anthropic`, `httpx2`, `httpcore2` y sus hijos— tengan **nivel efectivo INFO o superior**. No se usa `propagate=False`, para que avisos y errores sigan llegando al registro de la aplicación. No se define `ANTHROPIC_LOG`; la lista de permitidas lo rechaza.

   La aplicación configura también su propio registro para que se vea la línea INFO de metadatos del gateway, que hoy no aparece en `docker compose logs` (HALLAZGO 1 de #80).

   El test pone el logger raíz en DEBUG, ejercita una llamada con `httpx2.MockTransport` y comprueba que no se registra cuerpo ni clave y que un warning o error del SDK sigue propagándose. Si aparece contenido sensible a nivel INFO, se eleva el nivel mínimo a WARNING.

5. **Verificación en ACO-028.** Dos niveles, sin dependencias nuevas:

   - **Repositorio:** buscar el patrón `sk-ant-` en los ficheros versionados y en el historial (`git log -S'sk-ant-' --all` o `git grep` sobre `git rev-list --all`), comprobar que `.env` está ignorado y que `.env.example` no contiene valores. Puede ser un script, una comprobación de CI o una revisión documentada; no un test de aplicación.
   - **Aplicación:** una clave centinela no aparece en logs con el logger raíz en DEBUG, en respuestas HTTP (cuando exista ACO-030) ni en el código del frontend; solo el backend recibe la variable.

6. **Producción.** Este ADR declara que `.env` es solo para local y demo y no se autoriza en producción. El mecanismo de producción se decide en un ADR del Sprint 2: claves distintas por entorno y Docker secrets o un gestor gestionado, con rotación. El VPS es Sprint 2 y el proveedor puede condicionar la herramienta.

7. **Rotación e incidente.** Procedimiento manual para el Sprint 1: revocar y rotar la clave en Anthropic, actualizar `.env` o el almacén, reiniciar el backend y revisar logs y commits. Se documenta en el README. La rotación automática queda fuera de alcance.

8. **Alcance y secuencia.** Este ADR decide el mecanismo y los controles y se mergea antes de ampliar la ficha de ACO-028. La PR del ADR cierra #82. La ampliación de la ficha es el primer commit de la PR de ACO-028, y esa PR cierra #33. ACO-028 solo implementa y verifica lo decidido aquí, sin gestor nuevo ni dependencias. ACO-028 no entra en el hito del 27/10/2026.

## Alternativas consideradas

- **Docker secrets o fichero montado ahora:** descartada para local/demo; añade complejidad operativa sin mejorar el riesgo actual. Se valora en producción.
- **Gestor externo (Vault u otro) ahora:** descartada; añade un componente y una dependencia que el Sprint 1 no necesita.
- **Permitir `ANTHROPIC_BASE_URL` con una lista de proxies:** descartada; un proxy o endpoint alternativo requiere una decisión nueva, porque cambia la ruta de los datos.
- **Confiar en que Compose no pasa las variables:** descartada; no es un control y no cubre ejecuciones fuera de Compose.
- **Confiar en el entorno para proxies y certificados:** descartada; `trust_env=True` permite redirigir la conexión o instalar una CA, y el objetivo es que la clave no salga del endpoint previsto. Si en producción hace falta un proxy, se decidirá en el ADR del Sprint 2.
- **Lista de prohibidas en lugar de permitidas:** descartada; el SDK lee más variables de las identificadas y el rango `<2.0` puede añadir otras. La lista de permitidas falla de forma segura.
- **Impedir el arranque de la aplicación:** descartada; rompe el criterio AC-06 de ACO-027. `load_settings()` y `not_configured` consiguen el mismo efecto sin llamar al proveedor.
- **Confiar en el nivel INFO por defecto del SDK:** descartada; con el logger raíz en DEBUG se registra el cuerpo.
- **Desactivar por completo el logger del SDK:** descartada; oculta errores útiles.
- **Añadir un escáner de secretos (gitleaks o trufflehog):** aplazada; añade herramienta y mantenimiento. La búsqueda en el historial cubre la comprobación mínima sin dependencias.
- **Variables de entorno también en producción:** descartada; no es aceptable para un servicio con pacientes.
- **Rotación automática:** fuera de alcance del Sprint 1.
- **Omitir el ADR y decidir en la ficha de ACO-028:** descartada; contradice el Plan de Trabajo §9 y AGENTS.md.

## Consecuencias

- ACO-028 implementa la lista de permitidas en `load_settings()`, el `base_url` explícito, `open_telemetry=False`, el cliente `DefaultHttpxClient(trust_env=False)`, la configuración de logging al arrancar y sus tests. Su ficha debe recoger estos cambios, incluida la modificación del arranque de la aplicación.
- Cualquier variable `ANTHROPIC_*` nueva que el SDK lea y no esté permitida hará que el gateway falle con `not_configured` hasta que se revise. Es intencionado: obliga a decidir antes de aceptar una vía nueva de configuración.
- El guard se evalúa en cada llamada, no al importar, y registra solo el nombre de la variable. La clave sigue leyéndose únicamente en `get_api_key()`.
- La aplicación sigue arrancando sin clave y `/health` sigue respondiendo; el gateway falla con `not_configured` sin llamar al proveedor.
- La rotación de la clave personal debe confirmarse y documentarse como acción operativa; la PR de ACO-028 documentará el procedimiento. El README, el README del gateway, `.env.example` y `docker-compose.yml` se actualizan en ACO-028 si la implementación lo requiere.
- El mecanismo de producción, la rotación automática y el escáner de secretos quedan pendientes de decisiones posteriores.

## Fuera de esta decisión

- Mecanismo de producción (Sprint 2): Docker secrets, gestor gestionado, claves por entorno y rotación.
- Configuración de proxies o certificados corporativos; si hiciera falta, se decidirá en producción.
- Rotación automática y escáner de secretos en CI.
- Elección del modelo de Claude.
- Control de gasto, topes y crédito (otros ACOs).
- Exposición HTTP de errores o de la configuración (ACO-030).
- Detalles contractuales con ACANPAN sobre la cuenta y el titular de la clave.
- Autenticación y autorización de usuarios (ADR-011).

## Documentos afectados

Plan de Trabajo (§9, registro de ADR), README y README.es, README del gateway, `.env.example`, `docker-compose.yml` si la implementación lo requiere, ficha de ACO-028 (al ampliarla) y Documento Operativo Sprint 1 si cambia alguna estimación.
