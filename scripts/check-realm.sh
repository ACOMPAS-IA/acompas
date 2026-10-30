#!/usr/bin/env bash
# Comprueba el Keycloak local de ACOMPAS: el documento de descubrimiento OIDC
# del realm acompas, el cliente acompas-frontend y una petición de autorización
# hasta el formulario de login (ACO-012, ACO-013).
#
# Uso: scripts/check-realm.sh
# El puerto de Keycloak se toma de KEYCLOAK_PORT, del entorno o de .env (por
# defecto, 8080). Las credenciales de administrador se toman de
# KEYCLOAK_BOOTSTRAP_ADMIN_USER y KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD, del
# entorno o de .env (por defecto, los valores de desarrollo de Compose).
#
# El cliente está fijado en el JSON del realm con el puerto 5173 del frontend.
# Si se cambia FRONTEND_PORT, hay que actualizar el JSON y reimportar el realm.

set -euo pipefail

env_file="$(dirname "${BASH_SOURCE[0]}")/../.env"

# Lee una variable del entorno o de .env. Solo se extrae esa variable: no se
# hace source del fichero para no cargar las contraseñas.
env_value() {
  local name="$1"
  local value="${!name:-}"
  if [[ -z "${value}" && -f "${env_file}" ]]; then
    value="$(grep -E "^${name}=" "${env_file}" | tail -n1 | cut -d= -f2- || true)"
  fi
  printf '%s' "${value}"
}

port="$(env_value KEYCLOAK_PORT)"
port="${port:-8080}"
admin_user="$(env_value KEYCLOAK_BOOTSTRAP_ADMIN_USER)"
admin_user="${admin_user:-admin}"
admin_password="$(env_value KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD)"
admin_password="${admin_password:-acompas_dev}"

base_url="http://localhost:${port}"
discovery_url="${base_url}/realms/acompas/.well-known/openid-configuration"
expected_issuer="${base_url}/realms/acompas"
client_id="acompas-frontend"
redirect_uri="http://localhost:5173/auth/callback"
web_origin="http://localhost:5173"
auth_url="${base_url}/realms/acompas/protocol/openid-connect/auth"

if ! body="$(curl -fsS --max-time 5 "${discovery_url}")"; then
  echo "ERROR: el realm acompas no responde en ${discovery_url}" >&2
  exit 1
fi

if ! grep -q "\"issuer\":\"${expected_issuer}\"" <<<"${body}"; then
  echo "ERROR: el issuer no es ${expected_issuer}" >&2
  exit 1
fi

# Token de administrador del realm master para consultar la Admin API.
token_url="${base_url}/realms/master/protocol/openid-connect/token"
if ! token_response="$(curl -fsS --max-time 5 \
  -X POST "${token_url}" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'grant_type=password' \
  --data-urlencode 'client_id=admin-cli' \
  --data-urlencode "username=${admin_user}" \
  --data-urlencode "password=${admin_password}")"; then
  echo "ERROR: no se pudo obtener un token de administrador; revisa KEYCLOAK_BOOTSTRAP_ADMIN_USER y KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD" >&2
  exit 1
fi

access_token="$(grep -o '"access_token":"[^"]*"' <<<"${token_response}" | head -n1 | cut -d'"' -f4)"
if [[ -z "${access_token}" ]]; then
  echo "ERROR: la respuesta del token de administrador no contiene access_token" >&2
  exit 1
fi

clients_url="${base_url}/admin/realms/acompas/clients?clientId=${client_id}"
if ! clients_body="$(curl -fsS --max-time 5 -H "Authorization: Bearer ${access_token}" "${clients_url}")"; then
  echo "ERROR: no se pudo consultar el cliente ${client_id} por la Admin API" >&2
  exit 1
fi

client_count="$(grep -o "\"clientId\":\"${client_id}\"" <<<"${clients_body}" | wc -l | tr -d ' ')"
if [[ "${client_count}" -ne 1 ]]; then
  echo "ERROR: se esperaba un cliente ${client_id} y hay ${client_count}" >&2
  exit 1
fi

check_bool() {
  local field="$1"
  local expected="$2"
  if ! grep -Eq "\"${field}\"[[:space:]]*:[[:space:]]*${expected}" <<<"${clients_body}"; then
    echo "ERROR: el cliente ${client_id} no tiene ${field}: ${expected}" >&2
    exit 1
  fi
}

check_bool publicClient true
check_bool standardFlowEnabled true
check_bool implicitFlowEnabled false
check_bool directAccessGrantsEnabled false
check_bool serviceAccountsEnabled false
check_bool fullScopeAllowed true

if ! grep -Eq '"protocol"[[:space:]]*:[[:space:]]*"openid-connect"' <<<"${clients_body}"; then
  echo "ERROR: el cliente ${client_id} no usa el protocolo openid-connect" >&2
  exit 1
fi

extract_array() {
  local field="$1"
  grep -o "\"${field}\"[[:space:]]*:[[:space:]]*\[[^]]*\]" <<<"${clients_body}" | head -n1
}

redirects="$(extract_array redirectUris)"
if ! grep -q "\"${redirect_uri}\"" <<<"${redirects}"; then
  echo "ERROR: el cliente ${client_id} no tiene la redirección ${redirect_uri}" >&2
  exit 1
fi
if grep -q '\*' <<<"${redirects}"; then
  echo "ERROR: la redirección del cliente ${client_id} no debe usar comodines" >&2
  exit 1
fi

origins="$(extract_array webOrigins)"
if ! grep -q "\"${web_origin}\"" <<<"${origins}"; then
  echo "ERROR: el cliente ${client_id} no tiene el origen ${web_origin}" >&2
  exit 1
fi

scopes="$(extract_array defaultClientScopes)"
for scope in profile email roles web-origins acr basic; do
  if ! grep -q "\"${scope}\"" <<<"${scopes}"; then
    echo "ERROR: el cliente ${client_id} no tiene el scope ${scope}" >&2
    exit 1
  fi
done

if ! grep -Eq '"pkce\.code\.challenge\.method"[[:space:]]*:[[:space:]]*"S256"' <<<"${clients_body}"; then
  echo "ERROR: el cliente ${client_id} no exige PKCE S256" >&2
  exit 1
fi

if ! grep -Eq '"post\.logout\.redirect\.uris"[[:space:]]*:[[:space:]]*"http://localhost:5173/"' <<<"${clients_body}"; then
  echo "ERROR: el cliente ${client_id} no tiene la URI de cierre de sesión" >&2
  exit 1
fi

if grep -Eq '"secret"[[:space:]]*:[[:space:]]*"[^"]+"' <<<"${clients_body}"; then
  echo "ERROR: el cliente ${client_id} tiene secreto y debe ser público" >&2
  exit 1
fi

# Petición de autorización con el cliente y la redirección registrados. El
# code_challenge es sintético y válido como base64url de 43 caracteres.
query="client_id=${client_id}&response_type=code&scope=openid&state=acompas-check&code_challenge=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA&code_challenge_method=S256"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

valid_url="${auth_url}?${query}&redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Fauth%2Fcallback"
valid_code="$(curl -sS -L --max-time 5 -o "${tmp_dir}/login.html" -w '%{http_code}' "${valid_url}" || true)"
if [[ "${valid_code}" != "200" ]] || ! grep -Eq 'id="kc-form-login"|name="username"' "${tmp_dir}/login.html"; then
  echo "ERROR: la petición de autorización no devolvió el formulario de login (HTTP ${valid_code})" >&2
  exit 1
fi

invalid_url="${auth_url}?${query}&redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Fno-registrada"
invalid_code="$(curl -sS -L --max-time 5 -o "${tmp_dir}/invalid.html" -w '%{http_code}' "${invalid_url}" || true)"
if [[ "${invalid_code}" != "400" ]] || grep -Eq 'id="kc-form-login"|name="username"' "${tmp_dir}/invalid.html"; then
  echo "ERROR: una redirección no registrada no se rechazó como se esperaba (HTTP ${invalid_code})" >&2
  exit 1
fi

echo "OK: realm acompas, cliente ${client_id} y autorización verificados en ${base_url}"
