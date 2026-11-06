# Autenticación (ACO-014 y ACO-015)

Validación del JWT que emite Keycloak (ACO-012 y ACO-013) en el backend y
comprobación de la lista blanca del piloto (ACO-015). Protege los routers del
API que la declaran como dependencia. En el Sprint 1 son
`/api/conversation` (ACO-030) y `/api/anonymization` (ACO-024); `/health` sigue
siendo público.

## Contrato

La ficha fija el contrato en la sección 8. En resumen:

- firma RS256 con la clave del JWKS que corresponde al `kid`;
- `exp` obligatorio y sin margen de reloj;
- `iss` igual a `KEYCLOAK_ISSUER`;
- `azp` igual a `acompas-frontend`;
- `sub` obligatorio y con formato UUID;
- `typ` igual a `Bearer`;
- `aud` no se valida: el token de Keycloak lleva `aud: account` y la
  audiencia del cliente se comprueba por `azp`;
- roles de aplicación (`paciente`, `administrador`) en `realm_access.roles`;
- email del token presente en `EMAILS_AUTORIZADOS` (lista blanca del piloto,
  ACO-015). Se comprueba en cada petición después del JWT y del rol.

El email del token se conserva en el `Principal` y no se persiste: la
correspondencia email↔UUID es de Keycloak (ADR-001).

## Configuración

| Variable | Valor local | Significado |
| --- | --- | --- |
| `KEYCLOAK_ISSUER` | `http://localhost:${KEYCLOAK_PORT:-8080}/realms/acompas` | Valor esperado de `iss`. En Compose se deriva del puerto publicado. |
| `KEYCLOAK_JWKS_URL` | `http://keycloak:8080/realms/acompas/protocol/openid-connect/certs` | JWKS desde la red de Compose. Desde el anfitrión, `http://localhost:${KEYCLOAK_PORT:-8080}/...`. |
| `EMAILS_AUTORIZADOS` | `paciente@example.com` en `.env.example` (ejemplo sintético) | Direcciones autorizadas, separadas por comas (ACO-015). |

No hay valores por defecto en el código. Si faltan `KEYCLOAK_ISSUER` o
`KEYCLOAK_JWKS_URL`, el API responde 503 `auth_unavailable`. Si falta o está
vacía `EMAILS_AUTORIZADOS`, el API arranca y rechaza con 403. Los valores
locales están en `docker-compose.yml` y `.env.example`.

El issuer sigue a `KEYCLOAK_PORT`, porque en `start-dev` el `iss` depende del
host con el que el navegador llega a Keycloak. El JWKS no: va por la red de
Compose al puerto 8080 del contenedor, que no cambia con el puerto publicado.
Cambiar `KEYCLOAK_PORT` no exige tocar ninguna variable; `KEYCLOAK_ISSUER`
vacía en `.env` toma el valor derivado.

## Lista blanca del piloto (ACO-015)

`EMAILS_AUTORIZADOS` contiene las direcciones autorizadas separadas por comas.
Se lee del entorno en cada petición y se aplica `trim` y minúsculas a la lista
y al email del token; la comparación es exacta, sin comodines ni patrones de
dominio, y `*` es un carácter literal. Las entradas vacías se descartan.

- ausente o vacía: se rechaza a todos con 403 (cierre por defecto);
- token sin email: 403;
- email fuera de la lista: 403;
- email autorizado: se devuelve el `Principal` y continúa la petición.

El 403 es genérico (`{"detail": "forbidden"}`) y no registra el email ni el
`sub`. La lista no se expone por ningún endpoint y no se persiste. Al arrancar
se registra solo el número de direcciones distintas; si falta o está vacía, un
error con cero direcciones y el backend sigue en marcha.

En Compose, cambiar la lista exige recrear el servicio para que vuelva a leer
`.env` (`docker compose up -d backend`); un `restart` no basta.

Las comprobaciones heredadas de ACO-012 (P17: solo el administrador edita el
email) y ADR-016 (el usuario no obtiene tokens offline) se hacen a mano con
usuarios locales. No modifican este servicio.

## Respuestas

| Situación | Código | `detail` |
| --- | --- | --- |
| Token ausente, malformado o inválido (incluido un `kid` desconocido) | 401 | `unauthorized` |
| Token válido sin rol de aplicación | 403 | `forbidden` |
| Token válido con rol pero sin email, fuera de la lista o con lista vacía | 403 | `forbidden` |
| Configuración ausente o JWKS inaccesible o malformado | 503 | `auth_unavailable` |

Los 401 llevan `WWW-Authenticate: Bearer`. El cuerpo no incluye el token, sus
claims, el email ni el motivo concreto del rechazo, y nada de eso se registra
en logs.

La clasificación es por fase: primero se obtiene y valida el JWKS y después se
empareja el `kid` del token. Un fallo al obtener el JWKS es 503; un `kid` que
no existe en un JWKS correcto es 401. El refresco por `kid` desconocido está
acotado por una ventana de enfriamiento de 30 s.

### Caché del JWKS

El cliente guarda el JWKS durante 300 s. Mientras la caché es válida, el API
sigue validando con la clave cacheada aunque Keycloak esté caído; cuando
caduca, la siguiente petición devuelve 503 `auth_unavailable` hasta que el
JWKS vuelva a responder. Para el piloto es suficiente: la clave del realm no
cambia y una caída corta de Keycloak no interrumpe las peticiones en curso.

## Token para pruebas manuales

Hasta ACO-018 no hay forma de obtener un token real: los usuarios manuales de
ACO-015 son locales y no se versionan, y las concesiones directas están
desactivadas. Las pruebas manuales del endpoint se hacen con `pytest`:
`tests/auth` cubre el contrato con tokens sintéticos y `tests/conversation`
sustituye la autenticación para las pruebas de ACO-030.

Desde ACO-018:

1. inicia sesión en el frontend con el usuario sintético de ACO-015;
2. copia el `access_token` de la petición al token endpoint;
3. úsalo en `curl` o Postman con `Authorization: Bearer <token>`.

El token dura 300 s (ACO-012). No pegues tokens en issues, PRs, logs ni
capturas. La comprobación con token real de extremo a extremo es ACO-032.

## Pruebas

Los tests de `backend/tests/auth/` firman sus propios tokens con un par RSA
generado en el test y sustituyen el cliente del JWKS: no necesitan usuarios,
Keycloak ni red.

- `test_tokens.py`: validación de firma y claims.
- `test_jwks.py`: distinción entre JWKS no disponible (503) y `kid`
  desconocido (401), y refresco acotado.
- `test_api.py`: contrato HTTP del endpoint protegido y de `/health`.
- `test_whitelist.py`: normalización, comparación exacta, cierre por defecto y
  resumen de arranque sin valores.
- `test_whitelist_api.py`: acceso autorizado a conversación y anonimización,
  rechazo en ambos endpoints, retirada entre peticiones y contrato 401.
- `test_config.py`: variables obligatorias.
- `test_realm_contract.py`: coherencia con `infra/keycloak/import/acompas-realm.json`.
- `test_live.py`: comprobación manual del JWKS real; se ejecuta solo con
  `KEYCLOAK_LIVE=1` y no corre en la CI.
