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

- acción requerida por defecto `CONFIGURE_TOTP`, de modo que un usuario nuevo
  debe configurar su aplicación autenticadora en el primer acceso;
- 6 dígitos, periodo de 30 s, algoritmo `HmacSHA1` y ventana de anticipación 1,
  los valores por defecto de Keycloak.

No se usa WebAuthn ni SMS. La configuración se hace con la aplicación
autenticadora del usuario (TOTP).

### Política de contraseñas

`length(12) and notUsername and notEmail`: mínimo doce caracteres y prohibido
usar el nombre de usuario o el email como contraseña. No hay caducidad,
historial ni reglas de composición.

### Protección contra fuerza bruta

Activada (`bruteForceProtected: true`): el bloqueo temporal se dispara a los 5
fallos, con espera incremental de 60 s hasta un máximo de 900 s y sin bloqueo
permanente. No hay desbloqueo manual en el Sprint 1.

### Usuarios y clientes

El realm importado no contiene usuarios ni clientes de aplicación. Solo
aparecen los roles y clientes integrados de Keycloak. El cliente OIDC de
ACOMPAS es de ACO-013 y el alta y la lista blanca, de ACO-015.

## Importación y reimportación

`--import-realm` importa los ficheros de `import/` cuando el realm todavía no
existe. En un volumen nuevo, o en uno que aún no tenga el realm `acompas`, el
arranque lo crea:

```bash
docker compose up -d
```

Si el realm `acompas` ya existe, Keycloak **no lo sobrescribe**: los cambios
hechos en la consola se conservan y el JSON no se aplica. Para reconstruir el
realm desde el JSON hay que borrar el volumen y volver a arrancar:

```bash
docker compose rm -sf keycloak
docker volume rm acompas_keycloak_data
docker compose up -d
```

El prefijo del volumen es el nombre del directorio del proyecto (`acompas` por
defecto). Borrar el volumen elimina también los usuarios y los secretos TOTP
que se hayan creado a mano; en desarrollo no contiene datos reales.

## Comprobación

Con Keycloak en marcha:

```bash
scripts/check-realm.sh
```

El script comprueba el documento de descubrimiento OIDC del realm `acompas` y
su `issuer`. `scripts/check-keycloak.sh` sigue comprobando el realm `master`.

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
- Keycloak es el único custodio de la correspondencia email↔UUID; ACOMPAS no
  almacena el email (ADR-001).
- La lista blanca del piloto se guarda en la base de datos de ACOMPAS y no se
  implementa en Keycloak (ADR-009).
- Solo entorno local: sin TLS ni configuración de producción (ACO-011;
  ADR-011).
