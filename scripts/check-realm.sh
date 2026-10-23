#!/usr/bin/env bash
# Comprueba que el Keycloak local responde y publica el documento de
# descubrimiento OIDC del realm acompas (ACO-012).
#
# Uso: scripts/check-realm.sh
# El puerto se toma de KEYCLOAK_PORT, del entorno o de .env (por defecto, 8080).

set -euo pipefail

# Si KEYCLOAK_PORT no viene del entorno, se lee de .env. Solo se extrae esa
# variable: no se hace source del fichero para no cargar las contraseñas.
env_file="$(dirname "${BASH_SOURCE[0]}")/../.env"
if [[ -z "${KEYCLOAK_PORT:-}" && -f "${env_file}" ]]; then
  KEYCLOAK_PORT="$(grep -E '^KEYCLOAK_PORT=' "${env_file}" | tail -n1 | cut -d= -f2- || true)"
fi

port="${KEYCLOAK_PORT:-8080}"
base_url="http://localhost:${port}"
discovery_url="${base_url}/realms/acompas/.well-known/openid-configuration"
expected_issuer="${base_url}/realms/acompas"

if ! body="$(curl -fsS --max-time 5 "${discovery_url}")"; then
  echo "ERROR: el realm acompas no responde en ${discovery_url}" >&2
  exit 1
fi

if ! grep -q "\"issuer\":\"${expected_issuer}\"" <<<"${body}"; then
  echo "ERROR: el issuer no es ${expected_issuer}" >&2
  exit 1
fi

echo "OK: el realm acompas responde en ${base_url} (issuer ${expected_issuer})"
