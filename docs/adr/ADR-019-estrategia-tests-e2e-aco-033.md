# ADR-019 — Estrategia de tests E2E de ACO-033

Estado: aprobado

Sustituido por: —

Origen: Decisión conjunta #134 (cerrada el 11 de noviembre de 2026), que fija la herramienta (A1), los prerrequisitos (B1), la autenticación sin secretos (C1′) y el LLM simulado (D1′); y decisión conjunta #137 §D, que ordena este ADR antes de ampliar la ficha ejecutable de ACO-033. Issue #160. Implementación en ACO-033 (#38). Las acciones posteriores al merge tienen vehículo en #175 (precedente de #152).

Relacionados: ADR-020 (entorno de ejecución del backend con PyTorch; #135 y #159), ADR-006 (LLM gateway obligatorio), ADR-008 (sin datos reales), ADR-009 y ADR-017 (lista blanca), ADR-011 (autenticación y autorización), ADR-013 (política de anonimización y umbral), ADR-015 (gestión de secretos), ADR-005 y ADR-012 (no persistencia del original); ACO-026, ACO-032, ACO-033 y ACO-051; #63, #117 y #159.

## Contexto

El E2E de ACO-033 cubre el 2FA de T-14, además de T-17 (un email no autorizado recibe 403 genérico), T-21 (el disclaimer es visible), T-32 (caso feliz, usuario no autorizado y documento que no valida) y T-09 (ningún documento llega a la conversación sin pasar por la anonimización). En el cierre del Sprint 1, D-07 quedó como criterio no cumplido —los tests E2E no existían— y el ACO pasó al Sprint 2 con ese criterio heredado (`docs/arnes/08-PLAN.md:24,35`).

No hay ninguna pieza de E2E en el repositorio: `frontend/package.json` no tiene Playwright, no existen `frontend/e2e/` ni `backend/tests/e2e/`, y la CI ejecuta tres jobs —`backend`, `frontend` y `docs`— sin recorrer el flujo completo. El flujo que hay que probar lo fija ACO-032: login con 2FA → subida de un `.txt` sintético → anonimización → resultado → conversación → respuesta, dentro de `AppShell`.

La prueba es de contrato, no de detalle: lo que las pruebas unitarias no pueden cubrir son los saltos entre frontend, Keycloak y API —la redirección OIDC, el 2FA, el 403 de la lista blanca y el estado del documento entre pantallas—. Por eso recorre el flujo con el navegador y con el Keycloak reales, y solo sustituye lo que la CI no puede tener: el proveedor del LLM.

#134 decidió la herramienta, los prerrequisitos, la autenticación sin secretos y el LLM simulado. Este ADR fija cómo se ejecuta esa decisión. La imagen del backend y el entorno no se deciden aquí: son de ADR-020 y su implementación es #159. #159 condiciona el merge de ACO-033, no la redacción ni la aprobación de este ADR; D6 se cumple cuando #159 esté mergeado.

La estrategia no puede depender de piezas que la CI no tiene: ni datos de pacientes, ni la API key de Claude, ni usuarios con secretos fijos. Los tres se sustituyen por datos sintéticos, un gateway simulado y credenciales generadas en cada ejecución.

## Decisión

1. **Herramienta y ubicación (D1).** `@playwright/test` en TypeScript, como devDependency de `frontend/package.json`, con las pruebas en `frontend/e2e/` y solo el proyecto Chromium. La versión exacta queda clavada en `package-lock.json` y la fija la ficha de ACO-033; no forma parte del stack de producción. La instalación en CI es `npx playwright install --with-deps chromium`, sin imagen propia de Playwright. `frontend/e2e/` queda fuera de `tsconfig.app.json` y de Vitest, con `tsconfig.e2e.json` propio, y ESLint le da globals de Node en lugar de los del navegador.

2. **Entorno de ejecución (D2).** El `docker-compose.yml` real con un override `frontend/e2e/docker-compose.e2e.yml`:

   - el backend arranca con `uvicorn tests.e2e.app_e2e:app`;
   - la lista `EMAILS_AUTORIZADOS` lleva un solo email sintético autorizado;
   - los puertos son fijos y el navegador corre en el runner, no en un contenedor;
   - el frontend de Compose sigue reenviando `/api` al backend;
   - en CI los volúmenes se crean limpios, para que el realm se importe desde cero, y la espera es `docker compose up --wait` más `GET /health`.

3. **Autenticación sin secretos (D3).** Cada ejecución crea por la Admin API dos usuarios sintéticos con rol `paciente` y `CONFIGURE_TOTP`: uno con el email autorizado y otro con un email distinto, **fuera** de la lista, para el caso de acceso denegado. Los usuarios no se versionan ni se añaden al JSON del realm (ADR-008).

   La contraseña y la semilla TOTP son aleatorias, por usuario y ejecución. La semilla se inscribe en la página real de Keycloak leyendo el input oculto `#totpSecret` (o `#kc-totp-secret-key`). La Admin API no puede crear la credencial OTP: en Keycloak 26.8.0, `GET /admin/realms/acompas/users/{id}/credentials` responde 200 y `POST` a la misma ruta responde 404, medido el 17-nov-2026.

   Los códigos los calcula un helper de `frontend/e2e/` —nunca en `src/`— con `node:crypto`: HmacSHA1, 6 dígitos, periodo de 30 s y `lookAheadWindow` 1, la política del realm. El helper **no añade devDependency** y sustituye la que C1′ admitía declarar; queda escrito en la ficha.

   Las credenciales de administrador vienen del entorno (generadas en CI, `.env` en local) y nunca de Git. Los dos usuarios se borran al terminar, y ni la contraseña ni la semilla se escriben en logs ni en la salida de las pruebas.

4. **LLM simulado (D4).** `backend/tests/e2e/app_e2e.py` importa `app.main.app` y sustituye `get_llm_gateway` con `dependency_overrides` por un gateway determinista, con una respuesta fija que no contiene datos clínicos. Exige `ACOMPAS_E2E=1` para arrancar y no se usa en producción. `app/` no cambia y el job no recibe `ANTHROPIC_API_KEY`. Los umbrales de anonimización se fijan por entorno en el override, para que los casos no dependan de valores locales.

5. **Casos cubiertos (D5).** Tres: caso feliz (login con 2FA, documento sintético validado, conversación y respuesta con el disclaimer visible); usuario no autorizado (el login en Keycloak funciona y la API responde 403 genérico, que el cliente muestra como acceso denegado); y documento que no supera la validación (un `.txt` vacío produce `ilegible`, de forma determinista: el texto vacío es válido en el contrato y el servicio lo trata como ilegible).

   `retenido` queda fuera del E2E por coste y calibración del caso sintético —el umbral de documento es configurable por entorno (ADR-013)—, no por indeterminación, y se cubre en las pruebas unitarias de ACO-026. No se prueban otros navegadores ni viewports en esta fase.

6. **Integración en la CI (D6).** Un job `e2e` independiente en `.github/workflows/ci.yml`, en `pull_request` y en `push` a `main` como los demás y sin filtros de ruta. `timeout-minutes: 15`, `retries: 0`, traza y captura solo en fallo con retención corta, y caché de `~/.cache/ms-playwright` y de npm. El job construye la imagen del backend desde el `Dockerfile` del repositorio con los cambios de #159; si #159 publica la imagen en GHCR, consume esa imagen. Los 8–12 min son un umbral a medir, no una promesa. Convertir el job en check obligatorio no lo decide este ADR: lo configura la persona responsable.

7. **Datos y artefactos (D7).** Solo el corpus sintético de ACO-051 y ficheros generados en el directorio temporal del runner; ningún documento ni nombre de fichero real. La traza puede contener la página de inscripción con la semilla: se limita a la ejecución, con retención corta y usuario borrado al terminar, y no se comparte fuera del job. Los artefactos no incluyen texto de documentos en los commits ni en la descripción de la PR.

## Alternativas consideradas

- **Cypress:** descartada en #134 por la decisión A1; mantiene un runtime propio y otro modelo de asincronía.
- **Selenium:** descartada. Más piezas y más frágil para el flujo OIDC con redirecciones.
- **E2E sin navegador, solo contra la API:** descartada. No verifica T-14, T-21 ni el flujo de ACO-032, que son de interfaz.
- **Imagen oficial de Playwright como contenedor del job:** descartada. Añade una imagen que hay que versionar aparte; la instalación con `--with-deps` cubre lo necesario.
- **Inscribir el OTP por la Admin API:** descartada por la evidencia: la ruta de creación de credenciales no existe en Keycloak 26.8.0.
- **Simular Keycloak o el login:** descartada. T-14 exige el 2FA real; un mock dejaría sin probar el flujo que el criterio pide.
- **Semilla TOTP fija en el realm o en el repositorio:** descartada. Es un secreto en Git y contradice C1′ y ADR-015.
- **`otplib` como devDependency:** descartada. El helper con `node:crypto` cubre HmacSHA1 y 6 dígitos sin añadir dependencia.
- **Reintentos automáticos en CI:** descartados. Ocultan intermitencias; se prefiere traza y diagnóstico.
- **Probar contra el entorno de demo o un VPS:** descartada. Sale del alcance del sprint y no es reproducible en cada PR.

## Consecuencias

- `frontend/package.json` gana una devDependency y la CI, un job más. El flujo de ACO-032 pasa a verificarse en cada PR, no solo a mano.
- ACO-033 no se puede mergear antes que #159: el job necesita la imagen con torch CPU y los modelos, y sin ella la duración se dispara.
- No se añaden secretos: usuarios, contraseñas y semillas se generan y se destruyen en cada ejecución. No se usan datos reales.
- `app/` no cambia; la única pieza nueva del backend es la entrada de test `tests/e2e/app_e2e.py`, que ya viaja en la imagen porque el Dockerfile copia `tests/`.
- El ADR entra en el registro del Plan de Trabajo §9 al mergear y el arnés se regenera después; ambas acciones tienen vehículo en #175.
- La protección de rama y los checks obligatorios quedan como están hasta que la persona responsable decida incorporar el job `e2e`.

### Riesgos asumidos

- La inscripción del OTP leyendo `#totpSecret` depende del tema de Keycloak. La versión está fijada (26.8.0) y el identificador queda como contrato explícito.
- La prueba puede ser intermitente por tiempos de carga. Se mitiga con esperas por estado de la interfaz, `retries: 0` y traza en fallo, para ver la causa en vez de ocultarla.
- El job alarga la CI. El umbral de 8–12 min solo se puede medir con #159 mergeado; hasta entonces es una estimación.

## Fuera de esta decisión

- El alcance, los ficheros, los selectores y el número de pruebas de ACO-033: van en su ficha ejecutable.
- La imagen del backend con torch CPU y modelos precargados, y el entorno de ejecución: ADR-020, #159, #63 y #117.
- OCR y Niveles 2 y 3, y cualquier prueba sobre documentos reales.
- La protección de rama y la lista de checks obligatorios.

## Documentos afectados

- `docs/adr/ADR-019-estrategia-tests-e2e-aco-033.md` (este ADR)
- `docs/aco/ACO-033.md` (ampliación de la ficha ejecutable, después de este ADR)
- `.github/workflows/ci.yml` (job `e2e`)
- `frontend/package.json` y `frontend/package-lock.json` (devDependency)
- `frontend/e2e/` (pruebas, configuración y helper TOTP)
- `backend/tests/e2e/app_e2e.py` (entrada de test con el gateway simulado)
- Plan de Trabajo §9 (registro de ADR, después del merge; #175)
- Arnés (regeneración después del merge; #175)
