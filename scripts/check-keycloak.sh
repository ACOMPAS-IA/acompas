#!/usr/bin/env bash
# Comprueba que el Keycloak local responde y publica el documento de
# descubrimiento OIDC del realm master (ACO-011).
#
# Uso: scripts/check-keycloak.sh
# El puerto se toma de KEYCLOAK_PORT (por defecto, 8080).

set -euo pipefail

port="${KEYCLOAK_PORT:-8080}"
base_url="http://localhost:${port}"
discovery_url="${base_url}/realms/master/.well-known/openid-configuration"
expected_issuer="${base_url}/realms/master"

if ! body="$(curl -fsS --max-time 5 "${discovery_url}")"; then
  echo "ERROR: Keycloak no responde en ${discovery_url}" >&2
  exit 1
fi

if ! grep -q "\"issuer\":\"${expected_issuer}\"" <<<"${body}"; then
  echo "ERROR: el issuer no es ${expected_issuer}" >&2
  exit 1
fi

echo "OK: Keycloak responde en ${base_url} (issuer ${expected_issuer})"
