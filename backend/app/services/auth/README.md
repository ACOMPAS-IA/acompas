# Autenticación (ACO-014)

Validación del JWT que emite Keycloak (ACO-012 y ACO-013) en el backend.
Protege los routers del API que la declaran como dependencia. En el Sprint 1
es `/api/conversation` (ACO-030); `/health` sigue siendo público.

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
- roles de aplicación (`paciente`, `administrador`) en `realm_access.roles`.

El email del token se conserva en el `Principal` y no se persiste: la
correspondencia email↔UUID es de Keycloak (ADR-001).

## Configuración

| Variable | Valor local | Significado |
| --- | --- | --- |
| `KEYCLOAK_ISSUER` | `http://localhost:8080/realms/acompas` | Valor esperado de `iss`. |
| `KEYCLOAK_JWKS_URL` | `http://keycloak:8080/realms/acompas/protocol/openid-connect/certs` | JWKS desde la red de Compose. Desde el anfitrión, `http://localhost:8080/...`. |

No hay valores por defecto en el código: si faltan, el API responde 503
`auth_unavailable`. Los valores locales están en `docker-compose.yml` y
`.env.example`. Si cambias `KEYCLOAK_PORT`, actualiza las dos variables.

## Respuestas

| Situación | Código | `detail` |
| --- | --- | --- |
| Token ausente, malformado o inválido (incluido un `kid` desconocido) | 401 | `unauthorized` |
| Token válido sin rol de aplicación | 403 | `forbidden` |
| Configuración ausente o JWKS inaccesible o malformado | 503 | `auth_unavailable` |

Los 401 llevan `WWW-Authenticate: Bearer`. El cuerpo no incluye el token, sus
claims ni el motivo concreto del rechazo, y nada de eso se registra en logs.

La clasificación es por fase: primero se obtiene y valida el JWKS y después se
empareja el `kid` del token. Un fallo al obtener el JWKS es 503; un `kid` que
no existe en un JWKS correcto es 401. El refresco por `kid` desconocido está
acotado por una ventana de enfriamiento de 30 s.

## Pruebas

Los tests de `backend/tests/auth/` firman sus propios tokens con un par RSA
generado en el test y sustituyen el cliente del JWKS: no necesitan usuarios,
Keycloak ni red.

- `test_tokens.py`: validación de firma y claims.
- `test_jwks.py`: distinción entre JWKS no disponible (503) y `kid`
  desconocido (401), y refresco acotado.
- `test_api.py`: contrato HTTP del endpoint protegido y de `/health`.
- `test_config.py`: variables obligatorias.
- `test_realm_contract.py`: coherencia con `infra/keycloak/import/acompas-realm.json`.
- `test_live.py`: comprobación manual del JWKS real; se ejecuta solo con
  `KEYCLOAK_LIVE=1` y no corre en la CI.

La comprobación con un token real emitido por Keycloak corresponde a ACO-032,
con los usuarios de ACO-015.
