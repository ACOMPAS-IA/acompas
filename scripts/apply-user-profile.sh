#!/usr/bin/env bash
# Aplica la restricción del email del perfil de usuario del realm acompas:
# email.permissions.edit = ["admin"] (ACO-012 P17; ADR-017).
#
# El perfil de usuario no viaja en la representación del realm que importa
# --import-realm, así que se aplica después de la importación por la Admin API,
# limitado al endpoint del perfil del realm acompas.
#
# Uso: scripts/apply-user-profile.sh
# El puerto se toma de KEYCLOAK_PORT, del entorno o de .env (por defecto, 8080).
# La URL se construye siempre con localhost. Las credenciales de administrador
# se toman de KEYCLOAK_BOOTSTRAP_ADMIN_USER y
# KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD, del entorno o de .env (por defecto, los
# valores de desarrollo de Compose). No se hace source de .env ni se imprimen
# credenciales.

set -euo pipefail

if [[ "$#" -ne 0 ]]; then
  echo "ERROR: este script no admite argumentos ni opciones (incluido --force)" >&2
  echo "Uso: scripts/apply-user-profile.sh" >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: se requiere python3 para parchear el perfil de usuario" >&2
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

# Solo se admiten destinos locales: el script no acepta un host configurable.
base_url="http://localhost:${port}"
token_url="${base_url}/realms/master/protocol/openid-connect/token"
profile_url="${base_url}/admin/realms/acompas/users/profile"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT
token_file="${tmp_dir}/token.json"
profile_file="${tmp_dir}/profile.json"
desired_file="${tmp_dir}/profile-desired.json"
after_file="${tmp_dir}/profile-after.json"
put_response="${tmp_dir}/put-response.txt"

# Token de administrador del realm master para consultar la Admin API.
token_status="$(curl -sS -o "${token_file}" -w '%{http_code}' --max-time 5 \
  -X POST "${token_url}" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'grant_type=password' \
  --data-urlencode 'client_id=admin-cli' \
  --data-urlencode "username=${admin_user}" \
  --data-urlencode "password=${admin_password}" 2>/dev/null || true)"
if [[ "${token_status}" != "200" ]]; then
  echo "ERROR: no se pudo obtener un token de administrador en ${base_url}; revisa KEYCLOAK_BOOTSTRAP_ADMIN_USER y KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD y que Keycloak esté en marcha" >&2
  exit 1
fi

access_token="$(grep -o '"access_token":"[^"]*"' "${token_file}" | head -n1 | cut -d'"' -f4 || true)"
if [[ -z "${access_token}" ]]; then
  echo "ERROR: la respuesta del token de administrador no contiene access_token" >&2
  exit 1
fi

# GET del perfil completo. No se imprime su contenido.
profile_status="$(curl -sS -o "${profile_file}" -w '%{http_code}' --max-time 10 \
  -H "Authorization: Bearer ${access_token}" "${profile_url}" 2>/dev/null || true)"
if [[ "${profile_status}" == "000" || -z "${profile_status}" ]]; then
  echo "ERROR: Keycloak no responde en ${base_url}; ¿está arrancado?" >&2
  exit 1
fi
if [[ "${profile_status}" == "404" ]]; then
  echo "ERROR: el realm acompas no está importado (HTTP 404 en ${profile_url}); importa el realm y vuelve a ejecutar el script" >&2
  exit 1
fi
if [[ "${profile_status}" != "200" ]]; then
  echo "ERROR: no se pudo leer el perfil de usuario (HTTP ${profile_status})" >&2
  exit 1
fi

# Prepara el objeto completo con un único cambio: email.permissions.edit.
# Conserva view, groups y el resto de atributos. Si ya está aplicado, no escribe
# el fichero de destino y el script sale sin hacer PUT.
if ! patch_result="$(python3 - "${profile_file}" "${desired_file}" <<'PY'
import json
import sys

source_path, target_path = sys.argv[1], sys.argv[2]

try:
    with open(source_path, encoding="utf-8") as source:
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

email = email_attributes[0]
permissions = email.get("permissions")
if permissions is None:
    permissions = {}
    email["permissions"] = permissions
if not isinstance(permissions, dict):
    print("ERROR: email.permissions no es un objeto", file=sys.stderr)
    sys.exit(1)

if permissions.get("edit") == ["admin"]:
    print("already")
    sys.exit(0)

permissions["edit"] = ["admin"]

try:
    with open(target_path, "w", encoding="utf-8") as target:
        json.dump(profile, target, ensure_ascii=False, separators=(",", ":"))
except OSError as exc:
    print(f"ERROR: no se pudo escribir el perfil parcheado: {exc}", file=sys.stderr)
    sys.exit(1)

print("patched")
PY
)"; then
  echo "ERROR: no se pudo preparar el perfil; revisa que tenga el atributo email" >&2
  exit 1
fi

if [[ "${patch_result}" == "already" ]]; then
  echo "OK: el perfil ya tenía email.permissions.edit = [\"admin\"]; sin cambios"
  exit 0
fi

if [[ "${patch_result}" != "patched" ]]; then
  echo "ERROR: resultado inesperado al preparar el perfil" >&2
  exit 1
fi

# PUT del objeto completo. Keycloak devuelve 204 si actualiza el perfil.
put_status="$(curl -sS -o "${put_response}" -w '%{http_code}' --max-time 10 \
  -X PUT "${profile_url}" \
  -H "Authorization: Bearer ${access_token}" \
  -H 'Content-Type: application/json' \
  --data-binary @"${desired_file}" 2>/dev/null || true)"
if [[ "${put_status}" != "200" && "${put_status}" != "204" ]]; then
  echo "ERROR: no se pudo actualizar el perfil de usuario (HTTP ${put_status})" >&2
  exit 1
fi

# Relee el perfil y comprueba que el PUT dejó el valor esperado sin tocar view.
after_status="$(curl -sS -o "${after_file}" -w '%{http_code}' --max-time 10 \
  -H "Authorization: Bearer ${access_token}" "${profile_url}" 2>/dev/null || true)"
if [[ "${after_status}" != "200" ]]; then
  echo "ERROR: no se pudo releer el perfil después del PUT (HTTP ${after_status})" >&2
  exit 1
fi

if ! python3 - "${profile_file}" "${after_file}" <<'PY'
import json
import sys

before_path, after_path = sys.argv[1], sys.argv[2]


def load_profile(path):
    try:
        with open(path, encoding="utf-8") as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError):
        return None


def email_attribute(profile):
    if not isinstance(profile, dict):
        return None
    attributes = profile.get("attributes")
    if not isinstance(attributes, list):
        return None
    found = [
        attribute
        for attribute in attributes
        if isinstance(attribute, dict) and attribute.get("name") == "email"
    ]
    if len(found) != 1:
        return None
    return found[0]


before = load_profile(before_path)
after = load_profile(after_path)
before_email = email_attribute(before)
after_email = email_attribute(after)
if before_email is None or after_email is None:
    print("ERROR: el perfil no conserva exactamente un atributo email", file=sys.stderr)
    sys.exit(1)

before_permissions = before_email.get("permissions")
after_permissions = after_email.get("permissions")
if not isinstance(before_permissions, dict) or not isinstance(after_permissions, dict):
    print("ERROR: el perfil no conserva el objeto email.permissions", file=sys.stderr)
    sys.exit(1)

if after_permissions.get("edit") != ["admin"]:
    print("ERROR: email.permissions.edit no quedó en [\"admin\"]", file=sys.stderr)
    sys.exit(1)

if after_permissions.get("view") != before_permissions.get("view"):
    print("ERROR: email.permissions.view cambió al aplicar el perfil", file=sys.stderr)
    sys.exit(1)
PY
then
  echo "ERROR: el perfil no quedó con email.permissions.edit = [\"admin\"] y view sin cambios" >&2
  exit 1
fi

echo "OK: perfil de usuario del realm acompas actualizado: email.permissions.edit = [\"admin\"]; view sin cambios"
