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
| `fullScopeAllowed` | `true` |

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

## Comprobación

Con Keycloak en marcha y el realm reimportado:

```bash
scripts/check-realm.sh
```

El script comprueba:

- el documento de descubrimiento OIDC del realm `acompas` y su `issuer`;
- el cliente `acompas-frontend` por la Admin API: tipo, flujo, PKCE,
  redirección, origen, scopes, `fullScopeAllowed` y ausencia de secreto;
- una petición de autorización con el cliente y la redirección registrados, que
  debe devolver el formulario de login;
- una petición con una redirección no registrada, que debe rechazarse.

El script obtiene un token de administrador del realm `master` con
`KEYCLOAK_BOOTSTRAP_ADMIN_USER` y `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD`, del
entorno o de `.env` (por defecto, los valores de desarrollo de Compose). No
imprime el token ni la contraseña. No se añade a la CI: la CI actual no levanta
Keycloak.

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
