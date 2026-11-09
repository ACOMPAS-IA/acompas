# Keycloak

Configuración del Keycloak local de ACOMPAS. El servicio lo define
`docker-compose.yml` (ACO-011) y este directorio contiene el realm que se
importa al arrancar.

## Realm

El realm se define en `import/acompas-realm.json` y se importa con la opción
`--import-realm` del servicio `keycloak`.

| Ajuste | Valor |
| --- | --- |
| Realm | `acompas` |
| Nombre visible | `ACOMPAS` |
| HTTPS (`sslRequired`) | `external` (HTTP en local) |
| Registro (`registrationAllowed`) | `false` |
| Login con email (`loginWithEmailAllowed`) | `true` |
| Emails duplicados (`duplicateEmailsAllowed`) | `false` |
| Recuperación de contraseña (`resetPasswordAllowed`) | `false` |
| Verificación de email (`verifyEmail`) | `false` |
| Editar nombre de usuario (`editUsernameAllowed`) | `false` |
| Flujo browser (`browserFlow`) | `acompas-browser` (OTP obligatorio) |
| Idioma | `es` por defecto |
| Duración del token de acceso | 300 s |
| Sesión SSO inactiva / máxima | 1800 s / 36000 s |

### Roles

El realm define dos roles de aplicación:

- `paciente`;
- `administrador`.

Ninguno de los dos es rol por defecto: el rol `default-roles-acompas` de
Keycloak no los incluye. El rol `administrador` no concede acceso a la consola
de administración de Keycloak. La asignación del rol se hace en el alta del
usuario (ACO-015).

El rol por defecto `default-roles-acompas` se declara en el JSON como compuesto
por `uma_authorization` y por los roles de cliente `view-profile` y
`manage-account` del cliente `account`, sin `offline_access` (ACO-012 P16;
ADR-016). El JSON declara además `defaultRole` para que el rol por defecto
efectivo sea `default-roles-acompas` y no el `default-roles-acompas-1` que crea
el importador cuando falta ese campo (ACO-012 P18; ADR-018).

El importador de Keycloak 26.8.0 añade `offline_access` al rol por defecto
después de importar el JSON, así que el JSON no basta. Tras la importación hay
que ejecutar `scripts/apply-realm-config.sh`, que retira ese composite del rol
efectivo por la Admin API. El rol `offline_access` sigue existiendo en el realm,
pero ningún usuario lo hereda: solo se obtiene por asignación expresa.

### Perfil de usuario (email)

El perfil de usuario por defecto de Keycloak 26.8.0 permite al rol `user`
editar el email (`email.permissions.edit: ["admin","user"]`). Sin restricción,
quien pueda autenticarse podría cambiarlo por otro de la lista blanca y eludir
la comprobación del piloto. ADR-017 lo restringe a `["admin"]` (ACO-012 P17).

El perfil **no viaja en la representación del realm** que importa
`--import-realm`: no aparece en `GET /admin/realms/acompas` y las variantes
probadas no lo aplican. Por eso se aplica después de la importación, por la
Admin API y solo al endpoint del perfil:

```bash
scripts/apply-user-profile.sh
```

El script es idempotente, conserva `view` y el resto del perfil, usa las
credenciales de administrador de desarrollo de `.env` sin imprimir valores y no
añade dependencias: bash, curl y python3. Construye la URL solo con `localhost`
y `KEYCLOAK_PORT`; ADR-017 permite también `127.0.0.1`, pero esta implementación
no acepta otro destino ni una opción para forzarlo.

Una reimportación limpia borra el perfil y hay que volver a ejecutar el script.
`scripts/check-realm.sh` falla si `email.permissions.edit` no es exactamente
`["admin"]`. El procedimiento completo de post-importación, que incluye este
paso y el del rol por defecto, es `scripts/apply-realm-config.sh` (ver
«Importación y reimportación»).

### 2FA

El segundo factor es TOTP obligatorio para todos los usuarios del realm:

- flujo browser propio `acompas-browser`, con el formulario OTP como
  `REQUIRED`: el código se pide en todos los accesos, no solo cuando el usuario
  ya tiene una credencial OTP configurada;
- si el usuario no tiene OTP, el flujo le obliga a configurarlo antes de entrar.
  Esto cubre también a los usuarios creados por Admin API sin la acción
  `CONFIGURE_TOTP`;
- acción requerida por defecto `CONFIGURE_TOTP`, de modo que un usuario nuevo
  debe configurar su aplicación autenticadora en el primer acceso;
- `delete_credential` desactivada como defensa en profundidad. En Keycloak
  26.8.0 la consola de cuenta devuelve `removeable: false` y rechaza el borrado
  con `Credential type cannot be removed`. En todo caso, el borrado de la
  credencial por Admin API no permite entrar solo con contraseña: el siguiente
  login vuelve a exigir la configuración del OTP;
- 6 dígitos, periodo de 30 s, algoritmo `HmacSHA1` y ventana de anticipación 1,
  los valores por defecto de Keycloak.

No se usa WebAuthn ni SMS. La configuración se hace con la aplicación
autenticadora del usuario (TOTP). El flujo `browser` integrado de Keycloak es
condicional y no se usa como flujo del realm.

### Política de contraseñas

`length(12) and notUsername and notEmail`: mínimo doce caracteres y prohibido
usar el nombre de usuario o el email como contraseña. No hay caducidad,
historial ni reglas de composición.

### Protección contra fuerza bruta

Activada (`bruteForceProtected: true`): el bloqueo temporal se dispara a los 5
fallos, con espera incremental de 60 s hasta un máximo de 900 s y sin bloqueo
permanente. No hay desbloqueo manual en el Sprint 1.

### Usuarios y clientes

El realm importado no contiene usuarios. Contiene el cliente de aplicación
`acompas-frontend` (ACO-013) y los clientes integrados de Keycloak. El alta de
usuarios y la lista blanca son de ACO-015.

### Cliente OIDC `acompas-frontend`

El cliente de la SPA de ACOMPAS se declara en `import/acompas-realm.json`:

| Ajuste | Valor |
| --- | --- |
| Tipo | Público, sin secreto |
| Flujo | Authorization code |
| PKCE | `S256` obligatorio |
| Redirección | `http://localhost:5173/auth/callback` |
| Origen web | `http://localhost:5173` |
| Cierre de sesión | `http://localhost:5173/` |
| Scopes por defecto | `profile`, `email`, `roles`, `web-origins`, `acr`, `basic` |
| Scopes opcionales | Ninguno (`[]`); en particular, sin `offline_access` |
| `fullScopeAllowed` | `true` |

El cliente declara `optionalClientScopes` vacío para que no pueda pedir
`offline_access` ni obtener un token que sobreviva al cierre de sesión. El rol
`offline_access` ya no está en `default-roles-acompas`: se retiró en ACO-012
P16 (ADR-016) y ningún usuario lo hereda. Los clientes integrados de Keycloak
conservan sus propios scopes opcionales; sin el rol, el scope queda inerte.

El flujo implícito, la concesión directa de contraseña y las cuentas de
servicio están desactivados. La redirección `/auth/callback` es el contrato con
ACO-018, que implementa el login en el frontend. El cliente no crea usuarios ni
valida tokens: la validación del JWT es de ACO-014.

El puerto 5173 es el valor por defecto de `FRONTEND_PORT`. El JSON no lee
variables de entorno, así que si se cambia el puerto hay que actualizar
`redirectUris`, `webOrigins`, `rootUrl`, `baseUrl` y la URI de cierre de sesión,
y reimportar el realm.

## Importación y reimportación

`--import-realm` importa los ficheros de `import/` cuando el realm todavía no
existe. En un volumen nuevo, o en uno que aún no tenga el realm `acompas`, el
arranque lo crea:

```bash
docker compose up -d
```

Si el realm `acompas` ya existe, Keycloak **no lo sobrescribe**: los cambios
hechos en la consola se conservan y el JSON no se aplica. Esto incluye el
cliente `acompas-frontend` de ACO-013. Para reconstruir el realm desde el JSON
hay que borrar el volumen y volver a arrancar:

```bash
docker compose rm -sf keycloak
docker volume rm acompas_keycloak_data
docker compose up -d
```

El prefijo del volumen es el nombre del directorio del proyecto (`acompas` por
defecto). Borrar el volumen elimina también los usuarios y los secretos TOTP
que se hayan creado a mano; en desarrollo no contiene datos reales.

Este procedimiento aplica los cambios del JSON, pero no basta para el rol por
defecto: el importador añade `offline_access` después de importar (ACO-012 P16 y
P18; ADR-016 y ADR-018). La comprobación funcional de que una petición con
`scope=openid offline_access` no devuelve un refresh token offline requiere un
usuario con TOTP y se ejecuta en ACO-015.

El perfil de usuario no se reconstruye desde el JSON. Tampoco la retirada de
`offline_access` del rol por defecto, porque el importador lo añade después de
importar. Tras una importación limpia hay que aplicar los dos pasos, en este
orden, y comprobar el realm:

```bash
scripts/apply-realm-config.sh
scripts/check-realm.sh
```

`scripts/apply-realm-config.sh` llama en orden a
`scripts/apply-user-profile.sh` (P17) y a `scripts/apply-default-role.sh` (P18),
no admite argumentos ni opciones y se detiene al primer fallo. No incluye la
comprobación: por eso `scripts/check-realm.sh` se ejecuta aparte. Los dos
scripts individuales siguen disponibles para ejecutarlos por separado al
depurar.

Sin estos pasos, `check-realm.sh` falla: `email.permissions.edit` vuelve a
`["admin","user"]` y el rol por defecto efectivo sigue heredando
`offline_access`. Una reimportación limpia borra el perfil y exige repetir el
wrapper (ACO-012 P17 y P18; ADR-017 y ADR-018).

`scripts/apply-default-role.sh` solo retira el composite `offline_access` del
rol por defecto efectivo: no elimina el rol `offline_access`, no toca clientes,
scopes ni otros composites, no cambia el nombre del rol y es idempotente. Si el
realm se importó antes de fijar `defaultRole`, su rol efectivo puede ser
`default-roles-acompas-1` y faltarle `uma_authorization`; en ese caso hay que
reimportar desde un volumen limpio con el JSON actualizado, no basta con
ejecutar el script.

## Comprobación

Con Keycloak en marcha, el realm reimportado y el perfil de usuario aplicado:

```bash
scripts/check-realm.sh
```

El script comprueba:

- el documento de descubrimiento OIDC del realm `acompas` y su `issuer`;
- el cliente `acompas-frontend` por la Admin API con todos los valores de la
  sección 8: tipo, flujo, PKCE, nombre, estado, `rootUrl`, `baseUrl`,
  redirección y origen exactos, scopes por defecto exactos sin adicionales,
  scopes opcionales vacíos, `fullScopeAllowed` y ausencia de secreto;
- los composites del rol por defecto **efectivo** (`GET /admin/realms/acompas`
  → `defaultRole.name`, no un nombre fijo) por la Admin API: sin
  `offline_access` y con `uma_authorization`, `view-profile` y
  `manage-account`, sin exigir igualdad exacta del conjunto;
- que el rol `offline_access` sigue existiendo en el realm;
- el perfil de usuario por la Admin API: el atributo `email` existe y
  `email.permissions.edit` es exactamente `["admin"]` (ACO-012 P17; ADR-017);
- una petición de autorización con el cliente y la redirección registrados, que
  debe devolver el formulario de login;
- una petición con una redirección no registrada, que debe rechazarse;
- una petición con `scope=openid offline_access`, que debe rechazarse con
  `error=invalid_scope`.

El script obtiene un token de administrador del realm `master` con
`KEYCLOAK_BOOTSTRAP_ADMIN_USER` y `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD`, del
entorno o de `.env` (por defecto, los valores de desarrollo de Compose). No
imprime el token ni la contraseña. `scripts/apply-user-profile.sh` y
`scripts/apply-default-role.sh` usan las mismas credenciales y tampoco las
imprimen. No se añade a la CI: la CI actual no levanta Keycloak.

`scripts/check-keycloak.sh` sigue comprobando el realm `master`.

El puerto se toma de `KEYCLOAK_PORT`, del entorno o de `.env` (por defecto,
8080). Si se cambia `KEYCLOAK_PORT`, la URL del issuer también cambia.

## Issuer desde el anfitrión y desde Compose

En modo `start-dev` el issuer se deriva del host de la petición:

- desde el anfitrión: `http://localhost:8080/realms/acompas`;
- desde la red de Compose: `http://keycloak:8080/realms/acompas`.

ACO-012 no fija `KC_HOSTNAME`; ACO-014 elige la URL de descubrimiento y la
validación del issuer. Si ACO-014 necesita un issuer único, el cambio
corresponde a ACO-011 o a una ficha posterior.

## Límites

- No se guardan secretos, credenciales ni usuarios en el JSON (ACO-012 §7).
- El cliente `acompas-frontend` es público y no tiene secreto (ACO-013).
- Keycloak es el único custodio de la correspondencia email↔UUID; ACOMPAS no
  almacena el email (ADR-001).
- La lista blanca del piloto se guarda en la base de datos de ACOMPAS y no se
  implementa en Keycloak (ADR-009).
- Solo entorno local: sin TLS ni configuración de producción (ACO-011;
  ADR-011).
