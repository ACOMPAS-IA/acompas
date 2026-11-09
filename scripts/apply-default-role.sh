#!/usr/bin/env bash
# Retira el composite offline_access del rol por defecto efectivo del realm
# acompas (ACO-012 P18; ADR-018).
#
# El importador de Keycloak 26.8.0 añade offline_access al rol por defecto
# después de importar el JSON. El JSON declara defaultRole para que el rol
# efectivo sea default-roles-acompas, pero el composite solo se puede retirar
# después de la importación por la Admin API.
#
# Uso: scripts/apply-default-role.sh
# El puerto se toma de KEYCLOAK_PORT, del entorno o de .env (por defecto, 8080).
# La URL se construye siempre con localhost. Las credenciales de administrador
# se toman de KEYCLOAK_BOOTSTRAP_ADMIN_USER y
# KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD, del entorno o de .env (por defecto, los
# valores de desarrollo de Compose). No se hace source de .env ni se imprimen
# credenciales.
#
# El script no cambia el nombre del defaultRole, no añade composites y no toca
# clientes, scopes ni el resto del realm. Es idempotente.

set -euo pipefail

if [[ "$#" -ne 0 ]]; then
  echo "ERROR: este script no admite argumentos ni opciones (incluido --force)" >&2
  echo "Uso: scripts/apply-default-role.sh" >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: se requiere python3 para leer y verificar el rol por defecto" >&2
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
realm_url="${base_url}/admin/realms/acompas"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT
token_file="${tmp_dir}/token.json"
realm_file="${tmp_dir}/realm.json"
composites_file="${tmp_dir}/composites.json"
after_file="${tmp_dir}/composites-after.json"
role_file="${tmp_dir}/role.json"
payload_file="${tmp_dir}/payload.json"
response_file="${tmp_dir}/response.txt"

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

# GET del realm para obtener el rol por defecto efectivo.
realm_status="$(curl -sS -o "${realm_file}" -w '%{http_code}' --max-time 10 \
  -H "Authorization: Bearer ${access_token}" "${realm_url}" 2>/dev/null || true)"
if [[ "${realm_status}" == "000" || -z "${realm_status}" ]]; then
  echo "ERROR: Keycloak no responde en ${base_url}; ¿está arrancado?" >&2
  exit 1
fi
if [[ "${realm_status}" == "404" ]]; then
  echo "ERROR: el realm acompas no está importado (HTTP 404 en ${realm_url}); importa el realm y vuelve a ejecutar el script" >&2
  exit 1
fi
if [[ "${realm_status}" != "200" ]]; then
  echo "ERROR: no se pudo leer el realm acompas (HTTP ${realm_status})" >&2
  exit 1
fi

if ! default_role="$(python3 - "${realm_file}" <<'PY'
import json
import sys

path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as source:
        realm = json.load(source)
except (OSError, json.JSONDecodeError) as exc:
    print(f"ERROR: no se pudo leer el realm: {exc}", file=sys.stderr)
    sys.exit(1)

default_role = realm.get("defaultRole")
if not isinstance(default_role, dict) or not isinstance(default_role.get("name"), str) or not default_role["name"]:
    print("ERROR: el realm no declara un defaultRole con nombre", file=sys.stderr)
    sys.exit(1)

print(default_role["name"])
PY
)"; then
  echo "ERROR: el realm acompas no tiene un rol por defecto efectivo; reimporta el realm con el JSON actualizado (ADR-018)" >&2
  exit 1
fi

# El nombre del rol puede contener caracteres que no van en una URL; se
# codifica sin dependencias.
encoded_role="$(python3 - "${default_role}" <<'PY'
import sys
import urllib.parse

print(urllib.parse.quote(sys.argv[1], safe=""))
PY
)"
composites_url="${realm_url}/roles/${encoded_role}/composites"

composites_status="$(curl -sS -o "${composites_file}" -w '%{http_code}' --max-time 10 \
  -H "Authorization: Bearer ${access_token}" "${composites_url}" 2>/dev/null || true)"
if [[ "${composites_status}" != "200" ]]; then
  echo "ERROR: no se pudieron consultar los composites de ${default_role} (HTTP ${composites_status})" >&2
  exit 1
fi

has_offline="$(python3 - "${composites_file}" <<'PY'
import json
import sys

path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as source:
        composites = json.load(source)
except (OSError, json.JSONDecodeError) as exc:
    print(f"ERROR: no se pudieron leer los composites: {exc}", file=sys.stderr)
    sys.exit(1)

if not isinstance(composites, list):
    print("ERROR: la respuesta de composites no es una lista", file=sys.stderr)
    sys.exit(1)

print("yes" if any(item.get("name") == "offline_access" for item in composites if isinstance(item, dict)) else "no")
PY
)"

if [[ "${has_offline}" == "yes" ]]; then
  # Se envía la representación del rol offline_access, no solo el nombre.
  role_status="$(curl -sS -o "${role_file}" -w '%{http_code}' --max-time 10 \
    -H "Authorization: Bearer ${access_token}" \
    "${realm_url}/roles/offline_access" 2>/dev/null || true)"
  if [[ "${role_status}" != "200" ]]; then
    echo "ERROR: no se pudo leer el rol offline_access (HTTP ${role_status})" >&2
    exit 1
  fi

  if ! python3 - "${role_file}" "${payload_file}" <<'PY'
import json
import sys

role_path, payload_path = sys.argv[1], sys.argv[2]
try:
    with open(role_path, encoding="utf-8") as source:
        role = json.load(source)
except (OSError, json.JSONDecodeError) as exc:
    print(f"ERROR: no se pudo leer el rol offline_access: {exc}", file=sys.stderr)
    sys.exit(1)

if not isinstance(role, dict) or role.get("name") != "offline_access":
    print("ERROR: la representación del rol offline_access no es válida", file=sys.stderr)
    sys.exit(1)

with open(payload_path, "w", encoding="utf-8") as target:
    json.dump([role], target, ensure_ascii=False, separators=(",", ":"))
PY
  then
    echo "ERROR: no se pudo preparar la retirada de offline_access" >&2
    exit 1
  fi

  delete_status="$(curl -sS -o "${response_file}" -w '%{http_code}' --max-time 10 \
    -X DELETE "${composites_url}" \
    -H "Authorization: Bearer ${access_token}" \
    -H 'Content-Type: application/json' \
    --data-binary @"${payload_file}" 2>/dev/null || true)"
  if [[ "${delete_status}" != "204" && "${delete_status}" != "200" ]]; then
    echo "ERROR: no se pudo retirar offline_access de ${default_role} (HTTP ${delete_status})" >&2
    exit 1
  fi
  echo "OK: offline_access retirado de los composites de ${default_role}"
else
  echo "OK: ${default_role} ya no incluye offline_access; sin cambios"
fi

# Verificación posterior: el rol efectivo no debe heredar offline_access y debe
# conservar los composites declarados. Si el realm se importó antes de fijar
# defaultRole, el rol efectivo puede ser otro y faltarle uma_authorization: en
# ese caso hay que reimportar, y el script no lo corrige.
after_status="$(curl -sS -o "${after_file}" -w '%{http_code}' --max-time 10 \
  -H "Authorization: Bearer ${access_token}" "${composites_url}" 2>/dev/null || true)"
if [[ "${after_status}" != "200" ]]; then
  echo "ERROR: no se pudieron releer los composites de ${default_role} (HTTP ${after_status})" >&2
  exit 1
fi

if ! python3 - "${after_file}" "${default_role}" <<'PY'
import json
import sys

path, default_role = sys.argv[1], sys.argv[2]
try:
    with open(path, encoding="utf-8") as source:
        composites = json.load(source)
except (OSError, json.JSONDecodeError) as exc:
    print(f"ERROR: no se pudieron leer los composites: {exc}", file=sys.stderr)
    sys.exit(1)

if not isinstance(composites, list):
    print("ERROR: la respuesta de composites no es una lista", file=sys.stderr)
    sys.exit(1)

names = {item.get("name") for item in composites if isinstance(item, dict)}
if "offline_access" in names:
    print(f"ERROR: {default_role} sigue incluyendo offline_access", file=sys.stderr)
    sys.exit(1)

missing = [name for name in ("uma_authorization", "view-profile", "manage-account") if name not in names]
if missing:
    print(
        f"ERROR: {default_role} no conserva los composites {', '.join(missing)}; "
        "si el rol por defecto efectivo no es default-roles-acompas, reimporta el realm con el JSON actualizado (ADR-018)",
        file=sys.stderr,
    )
    sys.exit(1)
PY
then
  echo "ERROR: el rol por defecto efectivo ${default_role} no quedó sin offline_access y con uma_authorization, view-profile y manage-account" >&2
  exit 1
fi

echo "OK: rol por defecto efectivo ${default_role} sin offline_access; conserva uma_authorization, view-profile y manage-account"
