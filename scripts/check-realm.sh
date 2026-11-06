#!/usr/bin/env bash
# Comprueba el Keycloak local de ACOMPAS: el documento de descubrimiento OIDC
# del realm acompas, el cliente acompas-frontend, los composites del rol por
# defecto, el perfil de usuario, una petición de autorización hasta el
# formulario de login y el rechazo de offline_access (ACO-012, ACO-013).
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

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: se requiere python3 para comprobar el perfil de usuario" >&2
  exit 1
fi

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
if [[ ! "${port}" =~ ^[0-9]{1,5}$ ]]; then
  echo "ERROR: KEYCLOAK_PORT debe ser un número entre 1 y 65535" >&2
  exit 1
fi
port="$((10#${port}))"
if (( port < 1 || port > 65535 )); then
  echo "ERROR: KEYCLOAK_PORT debe ser un número entre 1 y 65535" >&2
  exit 1
fi
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

client_count="$(grep -Eo "\"clientId\"[[:space:]]*:[[:space:]]*\"${client_id}\"" <<<"${clients_body}" | wc -l | tr -d ' ')"
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

check_string() {
  local field="$1"
  local expected="$2"
  if ! grep -Eq "\"${field}\"[[:space:]]*:[[:space:]]*\"${expected}\"" <<<"${clients_body}"; then
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
check_bool enabled true
check_string name "ACOMPAS frontend"
check_string rootUrl "${web_origin}"
check_string baseUrl "${web_origin}"

if ! grep -Eq '"protocol"[[:space:]]*:[[:space:]]*"openid-connect"' <<<"${clients_body}"; then
  echo "ERROR: el cliente ${client_id} no usa el protocolo openid-connect" >&2
  exit 1
fi

extract_array() {
  local field="$1"
  grep -o "\"${field}\"[[:space:]]*:[[:space:]]*\[[^]]*\]" <<<"${clients_body}" | head -n1
}

array_values() {
  local field="$1"
  extract_array "${field}" | sed 's/^[^:]*://' | tr -d '[]"' | tr ',' '\n' \
    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sed '/^$/d' | sort
}

redirects="$(array_values redirectUris)"
if [[ "${redirects}" != "${redirect_uri}" ]]; then
  echo "ERROR: redirectUris debe ser exactamente [${redirect_uri}]" >&2
  exit 1
fi

origins="$(array_values webOrigins)"
if [[ "${origins}" != "${web_origin}" ]]; then
  echo "ERROR: webOrigins debe ser exactamente [${web_origin}]" >&2
  exit 1
fi

scopes="$(array_values defaultClientScopes)"
expected_scopes="$(printf '%s\n' profile email roles web-origins acr basic | sort)"
if [[ "${scopes}" != "${expected_scopes}" ]]; then
  echo "ERROR: defaultClientScopes debe ser exactamente [profile, email, roles, web-origins, acr, basic]" >&2
  exit 1
fi

optional_scopes="$(array_values optionalClientScopes)"
if [[ -n "${optional_scopes}" ]]; then
  echo "ERROR: optionalClientScopes debe estar vacío, sin offline_access" >&2
  exit 1
fi

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

# Rol por defecto del realm: sin offline_access y con los composites que
# conserva. Se consulta el realm en marcha, no solo el JSON (ADR-016, P16).
default_role="default-roles-acompas"
composites_url="${base_url}/admin/realms/acompas/roles/${default_role}/composites"
if ! composites_body="$(curl -fsS --max-time 5 \
  -H "Authorization: Bearer ${access_token}" "${composites_url}")"; then
  echo "ERROR: no se pudieron consultar los composites de ${default_role} por la Admin API" >&2
  exit 1
fi

# Extrae solo los nombres de la respuesta de composites. No se reutiliza el
# cuerpo de otra consulta y la comparación es exacta por línea, para no
# confundir offline_access con un rol de nombre parecido.
role_names() {
  grep -Eo '"name"[[:space:]]*:[[:space:]]*"[^"]*"' <<<"$1" \
    | sed 's/^"name"[[:space:]]*:[[:space:]]*"//;s/"$//' | sort -u
}

default_role_names="$(role_names "${composites_body}")"

if grep -Fxq 'offline_access' <<<"${default_role_names}"; then
  echo "ERROR: ${default_role} incluye offline_access" >&2
  exit 1
fi

for required_role in uma_authorization view-profile manage-account; do
  if ! grep -Fxq "${required_role}" <<<"${default_role_names}"; then
    echo "ERROR: ${default_role} no incluye el composite ${required_role}" >&2
    exit 1
  fi
done

# El rol offline_access debe seguir existiendo en el realm aunque ya no se
# herede por defecto.
offline_role_status="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 \
  -H "Authorization: Bearer ${access_token}" \
  "${base_url}/admin/realms/acompas/roles/offline_access" || true)"
if [[ "${offline_role_status}" != "200" ]]; then
  echo "ERROR: el rol offline_access no existe en el realm (HTTP ${offline_role_status})" >&2
  exit 1
fi

# Perfil de usuario del realm: el email solo lo puede editar el administrador
# (ACO-012 P17; ADR-017). Se consulta el realm en marcha, no el JSON.
tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT
profile_url="${base_url}/admin/realms/acompas/users/profile"
profile_status="$(curl -sS -o "${tmp_dir}/profile.json" -w '%{http_code}' --max-time 5 \
  -H "Authorization: Bearer ${access_token}" "${profile_url}" 2>/dev/null || true)"
if [[ "${profile_status}" == "000" || -z "${profile_status}" ]]; then
  echo "ERROR: Keycloak no responde al consultar el perfil de usuario en ${base_url}" >&2
  exit 1
fi
if [[ "${profile_status}" == "404" ]]; then
  echo "ERROR: el realm acompas no tiene perfil de usuario (HTTP 404); ¿está importado?" >&2
  exit 1
fi
if [[ "${profile_status}" != "200" ]]; then
  echo "ERROR: no se pudo consultar el perfil de usuario (HTTP ${profile_status})" >&2
  exit 1
fi
if ! python3 - "${tmp_dir}/profile.json" <<'PY'
import json
import sys

path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as source:
        profile = json.load(source)
except (OSError, json.JSONDecodeError) as exc:
    print(f"ERROR: no se pudo leer el perfil: {exc}", file=sys.stderr)
    sys.exit(1)

attributes = profile.get("attributes")
if not isinstance(attributes, list):
    print("ERROR: el perfil no contiene una lista de atributos", file=sys.stderr)
    sys.exit(1)

email_attributes = [
    attribute
    for attribute in attributes
    if isinstance(attribute, dict) and attribute.get("name") == "email"
]
if len(email_attributes) != 1:
    print("ERROR: el perfil debe tener exactamente un atributo email", file=sys.stderr)
    sys.exit(1)

permissions = email_attributes[0].get("permissions")
if not isinstance(permissions, dict):
    print("ERROR: el atributo email no tiene el objeto permissions", file=sys.stderr)
    sys.exit(1)

if permissions.get("edit") != ["admin"]:
    print(
        f"ERROR: email.permissions.edit debe ser [\"admin\"] y es {permissions.get('edit')!r}",
        file=sys.stderr,
    )
    sys.exit(1)
PY
then
  echo "ERROR: el perfil de usuario no tiene email.permissions.edit = [\"admin\"] (ACO-012 P17; ADR-017)" >&2
  exit 1
fi

# Petición de autorización con el cliente y la redirección registrados. El
# code_challenge es sintético y válido como base64url de 43 caracteres.
query="client_id=${client_id}&response_type=code&scope=openid&state=acompas-check&code_challenge=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA&code_challenge_method=S256"

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

# El cliente no debe poder pedir offline_access. Si lo tuviera asignado, la
# petición mostraría el formulario de login; sin él, Keycloak redirige con
# error=invalid_scope.
offline_query="client_id=${client_id}&response_type=code&scope=openid%20offline_access&state=acompas-check&code_challenge=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA&code_challenge_method=S256"
offline_url="${auth_url}?${offline_query}&redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Fauth%2Fcallback"
offline_headers="$(curl -sS -D - -o /dev/null --max-time 5 "${offline_url}" || true)"
if ! grep -Eiq '^location:.*error=invalid_scope' <<<"${offline_headers}"; then
  echo "ERROR: el cliente ${client_id} admite el scope offline_access" >&2
  exit 1
fi

echo "OK: realm acompas, cliente ${client_id}, rol por defecto, perfil de usuario, autorización y offline_access verificados en ${base_url}"
