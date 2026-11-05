# ADR-017 — Mecanismo de la lista blanca del piloto

Estado: aprobado

Sustituido por: —

Origen: Decisión conjunta #102 (3–5 nov 2026; sin objeción registrada al vencer el plazo), con las tres condiciones de Luis del Olmo. La aplicación posterior al import mediante Admin API, acotada al perfil de usuario del realm `acompas` en local/demo, queda autorizada por #102 como precisión de su condición 3. Implementación en ACO-015 (#20) y ACO-012 P17.

Relacionados: ADR-009 (lista blanca), ADR-011 (autenticación y autorización), ADR-015 (gestión de secretos), ADR-016 (retirada de `offline_access`), ADR-001 (Keycloak como custodio email↔UUID); ACO-012, ACO-014 y ACO-015.

## Contexto

ADR-009 decidió que, durante el piloto, la lista blanca se guarda en la base de datos de ACOMPAS, que la gestiona manualmente el administrador y que Keycloak solo resuelve o crea el UUID de un email autorizado. Dejó expresamente fuera de su decisión **cómo se comprueba la lista** y **cómo se conecta con el login**.

Hoy no hay ninguna capa de base de datos en el backend: no hay SQLAlchemy ni Alembic, el servicio `postgres` existe en Compose pero el backend no lo usa y su única inicialización crea la extensión `vector`. El modelo relacional definitivo, el DDL y las migraciones son del Sprint 2 (ACO-035–046). ACO-015 está estimado en 2–3 h, que no cubren estrenar esa capa, una migración, la comprobación y sus tests.

Hechos que enmarcan la decisión:

- El realm `acompas` no tiene usuarios y `registrationAllowed` es `false`: los usuarios solo se crean por el administrador (ACO-012 P2; ADR-009).
- ACO-014 (PR #100) introduce la validación del JWT y un `Principal` con UUID, email opcional y roles. El email del token es el dato disponible para comprobar la lista y no se persiste.
- El cliente `acompas-frontend` incluye el scope `email` entre los scopes por defecto (ACO-013), así que el token lleva el claim.
- Verificado el 4-nov-2026 con Keycloak 26.8.0 en local: el perfil de usuario por defecto permite al rol `user` editar `email` (`permissions.edit: ["admin","user"]`). Sin restricción, quien pueda autenticarse puede cambiar su email por otro de la lista y eludir la comprobación.
- Verificado en la misma fecha: la configuración del perfil de usuario **no viaja en la representación del realm** que importa `--import-realm`. No aparece en `GET /admin/realms/acompas`, `RealmRepresentation` no tiene campo para ella y las variantes probadas (`attributes["declarative-user-profile"]`, `userProfile`) no la aplican. Hay que aplicarla después de la importación por la Admin API.
- Es un cambio de seguridad: requiere decisión conjunta y ADR (Plan de Trabajo §8 y §9).

## Decisión

1. **Dónde vive la lista (D1-A).** En la variable de entorno `EMAILS_AUTORIZADOS` del backend, en el `.env` local no versionado, como direcciones separadas por comas. `.env.example` solo lleva un ejemplo con dominio `example.com`. Ningún email real entra en el repositorio. Es una **excepción temporal a ADR-009**, limitada a local y demo, no a producción; la lista vuelve a la tabla `EMAIL_AUTORIZADO` en el Sprint 2. La lista no se devuelve por ningún endpoint ni se escribe en logs.

2. **Dónde se comprueba (D2-A).** En el backend, en cada petición protegida, después de validar el JWT y comprobar el rol de aplicación, comparando `Principal.email` con la lista. Un token sin email, un email que no está en la lista o una lista ausente o vacía producen **403** con cuerpo genérico (`forbidden`), sin distinguir el motivo para no permitir enumeración. Un usuario retirado de la lista pierde el acceso en la siguiente petición, sin esperar a que caduque el token.

3. **Demostración del rechazo (D3-A).** La demostración usa un usuario sintético de Keycloak con un email fuera de la lista, creado a mano solo en el entorno local, documentado como sintético y sin relación con pacientes ni con datos reales. Se usa en el ensayo del 6, en la demo del 9 y en ACO-033. La petición sin token (401) se mantiene como caso adicional (D3-B). El usuario sintético no forma parte de la lista ni del código del ACO.

4. **Normalización y cierre por defecto.** Se aplica `trim` y minúsculas a la lista y al email del token antes de comparar. La comparación es exacta: sin comodines, sin patrones de dominio y sin coincidencia parcial; un `*` se trata como carácter literal y nunca coincide. Si la variable falta o está vacía, el arranque registra un error claro con la lista a cero y el backend sigue en marcha rechazando a todos con 403; nunca permite a todos. El arranque registra solo el número de direcciones, nunca sus valores. Un rechazo normal no deja registro del email ni del `sub`; como mucho, una cuenta agregada sin identidad. Si se necesita trazabilidad puntual de un caso, se decide fuera de este ADR.

5. **Email editable solo por el administrador (condición 3 de #102).** Se restringe `email.permissions.edit` a `["admin"]` en el perfil de usuario del realm. Como el perfil no se puede declarar en el JSON del realm, se aplica después de la importación con `scripts/apply-user-profile.sh`:

   - idempotente: GET del perfil, parche de solo `email.permissions.edit` y PUT; no reemplaza el resto del perfil;
   - limitado al endpoint del perfil del realm `acompas`;
   - usa las credenciales de administrador de desarrollo que ya existen en `.env` y que `check-realm.sh` ya emplea para leer;
   - construye la URL con `localhost` o `127.0.0.1` y rechaza cualquier otro destino, **sin opción de forzarlo**;
   - sin dependencias nuevas; el parcheo del JSON usa `python3`, ya presente en el entorno de desarrollo;
   - falla con código distinto de cero y un mensaje claro si no puede aplicarlo o si el realm no está importado.

   `scripts/check-realm.sh` verifica que `email.permissions.edit` es exactamente `["admin"]` y no imprime credenciales ni contenido de `.env`. `infra/keycloak/README.md` documenta el paso como obligatorio tras cada importación limpia y lo añade al procedimiento de reimportación.

6. **Vehículo y orden.** La lista y su comprobación se implementan en ACO-015, sobre el `Principal` de ACO-014. La restricción del perfil es una corrección de ACO-012, P17, en una **PR separada de la de #99**; ADR-016 ya está abierto y ADR-017 debe estar mergeado antes. No hay reimportación adicional: el perfil se aplica al realm en marcha por API. Orden: ADR-017 → PR de P17 → ACO-015. P17 se ejecuta **después** de la reimportación de P16, porque recrear el volumen devuelve el realm al JSON y borra el perfil. ACO-015 espera también a que ACO-014 esté mergeado.

7. **Alcance.** No se introduce SQLAlchemy, Alembic, migración ni tabla. No se guarda la correspondencia email↔UUID en ACOMPAS. Keycloak sigue siendo el proveedor de identidad. No se toca el frontend, el flujo OIDC, los roles del realm ni la CI. Las pruebas usan tokens y direcciones sintéticas.

## Alternativas consideradas

- **D1-B (tabla `EMAIL_AUTORIZADO` ahora):** descartada. Estrena la capa de BD y una migración antes de que el modelo definitivo esté decidido (Sprint 2), y obliga a reestimar ACO-015 por encima del 50 %, con riesgo para el ensayo del 6. Un atajo con `psycopg` y un `CREATE TABLE` en la inicialización cabría en horas, pero se salta Alembic y el modelo definitivo, que es justo lo que B aporta, y crearía deuda para el Sprint 2.
- **D1-C (solo Keycloak):** descartada. No cumple ADR-009 y no implementa la comprobación de D-02; exigiría cambiar ADR-009.
- **D2-B (comprobar solo en el login):** descartada. No hay endpoint de sesión y un usuario retirado conservaría el acceso hasta que caduque el token.
- **D2-C (autenticador propio en Keycloak):** descartada. Añade un componente Java y queda fuera del alcance de ACO-015.
- **D3-B (solo petición sin token):** insuficiente para demostrar la lista blanca; se mantiene como caso adicional.
- **D3-C (usuario no autorizado sin cuenta):** demuestra la puerta cerrada, no la comprobación de ACOMPAS.
- **Aplicar el perfil a mano en la consola:** descartada. Rompe la reproducibilidad que ACO-012 exige y deja el paso a merced de que alguien lo recuerde; el check lo detectaría, pero no lo corregiría.
- **Reemplazar el perfil completo por un fichero versionado:** descartada. Congela los valores por defecto de 26.8.0 y se rompe en una actualización; el parche de un solo atributo es más robusto.
- **Lista por `sub` en vez de por email:** descartada. Exigiría guardar la correspondencia email↔UUID en ACOMPAS, contra ADR-009 y ADR-001.
- **Comodines o patrones de dominio:** descartados. Amplían el acceso y complican la normalización.
- **Permitir a todos si falta la variable:** descartada. Rompe el cierre por defecto que exige #102.
- **Negarse a arrancar si falta la variable:** descartada. Es igual de seguro, pero convierte un error de `.env` en una caída total y quita el 403 que pide #102; el error visible y el rechazo a todos son más diagnosticables.
- **Permitir `--force` para destinos no locales:** descartada. Un script que muta configuración de seguridad no debe poder apuntar a un entorno compartido por error; si algún día hace falta otro entorno, será con un procedimiento y una decisión propios.

## Consecuencias

- Excepción temporal a ADR-009. Se pierden `autorizado_por`, `usado` y `creado_en`: la lista no tiene auditoría propia más allá del fichero. La sustitución por la tabla y su migración quedan para el Sprint 2.
- Cambiar la lista exige recrear el servicio `backend` para que Compose vuelva a leer `.env`; un `restart` no basta. El administrador debe mantener sincronizados `.env` y los usuarios de Keycloak: un usuario de Keycloak que no esté en la lista recibe 403, y un email de la lista sin cuenta no puede autenticarse.
- La comprobación depende del claim `email` y del scope `email` del cliente. Un token sin email se rechaza; si el cliente dejara de pedir el scope, todos quedarían fuera, y los tests lo cubren.
- La restricción del perfil cierra la vía de cambiar el email desde la consola de cuenta, que era el riesgo identificado en #102. `manage-account` puede seguir en el rol por defecto.
- El realm deja de ser reconstruible solo desde el JSON importado: el perfil requiere el paso posterior. Es un uso acotado y deliberado de la Admin API, limitado al endpoint del perfil y a local/demo, y no reabre el resto de ACO-012 §5.
- Cualquier importación limpia posterior borra el perfil y exige volver a ejecutar el script. El README lo recoge y `check-realm.sh` lo detecta.
- No se añaden dependencias ni se modifica la CI. Las pruebas no usan red ni datos reales.
- La estimación de ACO-015 no cambia (D5); P17 se ejecuta como corrección de ACO-012 y su coste se registra en su PR.

## Fuera de esta decisión

- Producción y uso con datos reales; la lista de producción y su gestión.
- SMTP, verificación de email y recuperación de contraseña.
- Gestión completa de usuarios, autorregistro y altas autoservicio.
- La tabla `EMAIL_AUTORIZADO`, su migración y la capa de base de datos (Sprint 2).
- El frontend, el flujo OIDC y el cliente `acompas-frontend`.
- Los roles del realm y la retirada de `offline_access` (ADR-016).
- Un autenticador propio de Keycloak o cambios en sus flujos.
- La CI y el despliegue de Keycloak fuera del entorno local.

## Documentos afectados

- `backend/` (configuración, comprobación y tests de la lista blanca)
- `.env.example`
- `docs/aco/ACO-015.md` (puntos P1–Pn)
- `docs/aco/ACO-012.md` (P17)
- `scripts/apply-user-profile.sh`
- `scripts/check-realm.sh`
- `infra/keycloak/README.md`
- Plan de Trabajo §9 (registro de ADR)
