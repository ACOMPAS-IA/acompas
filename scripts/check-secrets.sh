#!/usr/bin/env bash
# Comprueba los controles de repositorio de la API key de Claude (ACO-028,
# ADR-015 §5 y T-39):
#   - el prefijo de las claves de Anthropic no aparece en archivos rastreados,
#     en el índice ni en el historial, salvo las menciones documentales
#     conocidas y este propio script;
#   - ninguna cadena con forma de clave real aparece en ninguna de esas
#     superficies, sin excepciones;
#   - .env está ignorado y no versionado;
#   - .env.example tiene vacías las variables del gateway que declara
#     GATEWAY_ENV_VARS, y ninguna otra;
#   - docker-compose.yml solo pasa esas variables al servicio backend;
#   - el frontend no contiene referencias a la configuración de Anthropic.
#
# No inspecciona archivos no versionados: .env contiene la clave real en local
# y no debe leerse.
#
# Uso: scripts/check-secrets.sh
# Se puede ejecutar desde cualquier directorio del repositorio.

set -euo pipefail

repo_root="$(git -C "$(dirname "${BASH_SOURCE[0]}")/.." rev-parse --show-toplevel)"
cd "${repo_root}"

if [[ "$(git rev-parse --is-shallow-repository)" == "true" ]]; then
  echo "ERROR: el clon es shallow; se necesita el historial completo (fetch-depth: 0)." >&2
  exit 1
fi

# El prefijo se escribe una sola vez; este script queda excluido de su propia
# búsqueda literal porque contiene el patrón.
literal_prefix='sk-ant-'
# Forma de una clave real: el prefijo seguido de 16 o más caracteres válidos.
real_key_pattern='sk-ant-[A-Za-z0-9_-]{16,}'

# Menciones documentales conocidas del prefijo. La búsqueda de forma real no
# tiene excepciones, así que una clave real en estos archivos seguiría
# detectándose.
excludes=(
  ':(exclude)docs/adr/ADR-015-gestion-secretos-api-key-claude.md'
  ':(exclude)docs/arnes/09-TESTS.md'
  ':(exclude)scripts/check-secrets.sh'
)

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

# 1. Prefijo literal en el árbol de trabajo de archivos rastreados.
if git grep -n -I -F "${literal_prefix}" -- . "${excludes[@]}"; then
  fail "el prefijo de las claves de Anthropic aparece en archivos rastreados"
fi

# 2. Prefijo literal en el índice.
if git grep --cached -n -I -F "${literal_prefix}" -- . "${excludes[@]}"; then
  fail "el prefijo de las claves de Anthropic aparece en el índice"
fi

# 3. Prefijo literal en el historial.
history_literal="$(git log --all -S"${literal_prefix}" --format='%h %s' -- . "${excludes[@]}")"
if [[ -n "${history_literal}" ]]; then
  echo "${history_literal}" >&2
  fail "el prefijo de las claves de Anthropic aparece en el historial"
fi

# 4. Forma de clave real en el árbol de trabajo, el índice y el historial, sin
#    excepciones.
if git grep -n -I -E "${real_key_pattern}" -- .; then
  fail "una cadena con forma de clave real aparece en archivos rastreados"
fi

if git grep --cached -n -I -E "${real_key_pattern}" -- .; then
  fail "una cadena con forma de clave real aparece en el índice"
fi

history_real="$(git log --all -G"${real_key_pattern}" --format='%h %s' -- .)"
if [[ -n "${history_real}" ]]; then
  echo "${history_real}" >&2
  fail "una cadena con forma de clave real aparece en el historial"
fi

# 5. .env ignorado y no versionado.
grep -qx '.env' .gitignore || fail ".gitignore no contiene .env"
git check-ignore -q .env || fail ".env no está ignorado por Git"
if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  fail ".env está versionado"
fi

# 6. Variables del gateway: la lista sale de config.py (#107) y .env.example
#    las tiene presentes, vacías y sin sobrantes.
gateway_vars=()
while IFS= read -r name; do
  gateway_vars+=("${name}")
done < <(
  sed -n '/^GATEWAY_ENV_VARS = (/,/^)/p' \
    backend/app/services/llm_gateway/config.py \
    | grep -oE '"[A-Z0-9_]+"' | tr -d '"'
)
if (( ${#gateway_vars[@]} < 5 )); then
  fail "no se pudo leer GATEWAY_ENV_VARS de backend/app/services/llm_gateway/config.py"
fi
for name in "${gateway_vars[@]}"; do
  [[ "${name}" =~ ^(ANTHROPIC_|LLM_)[A-Z0-9_]+$ ]] \
    || fail "GATEWAY_ENV_VARS contiene un nombre inesperado: ${name}"
done

for name in "${gateway_vars[@]}"; do
  grep -qx "${name}=" .env.example || fail ".env.example no tiene ${name}= vacía"
done
if grep -Eq '^(ANTHROPIC_|LLM_)[A-Z0-9_]+=.+' .env.example; then
  fail ".env.example contiene un valor para una variable del gateway"
fi
while IFS= read -r declared; do
  [[ -z "${declared}" ]] && continue
  printf '%s\n' "${gateway_vars[@]}" | grep -qx "${declared}" \
    || fail ".env.example declara ${declared}, que no está en GATEWAY_ENV_VARS"
done < <(grep -oE '^(ANTHROPIC_|LLM_)[A-Z0-9_]+' .env.example || true)

# 7. docker-compose.yml: las variables del gateway solo en el servicio backend.
for name in "${gateway_vars[@]}"; do
  grep -q "^[[:space:]]*${name}:" docker-compose.yml \
    || fail "docker-compose.yml no pasa ${name}"
done
if ! awk '
  /^  [A-Za-z0-9_-]+:/ { service = $1; sub(":", "", service) }
  /^[[:space:]]+(ANTHROPIC_|LLM_)[A-Z0-9_]+:/ {
    if (service != "backend") {
      print "ERROR: " $1 " en el servicio " service > "/dev/stderr"
      bad = 1
    }
  }
  END { exit bad }
' docker-compose.yml; then
  fail "docker-compose.yml pasa variables del gateway a un servicio distinto de backend"
fi

# 8. El frontend no recibe ni menciona la configuración de Anthropic.
if git grep -n -I -E 'ANTHROPIC_|sk-ant-' -- frontend; then
  fail "el frontend contiene referencias a la configuración de Anthropic"
fi

echo "OK: controles de repositorio de la API key verificados"
