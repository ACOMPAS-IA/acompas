#!/usr/bin/env bash
# Aplica, después de una importación limpia del realm acompas, los cambios que
# no viajan en la representación del realm que importa --import-realm:
# el perfil de usuario (ACO-012 P17; ADR-017) y el rol por defecto efectivo
# (ACO-012 P18; ADR-018).
#
# Uso: scripts/apply-realm-config.sh
#
# Llama en orden a scripts/apply-user-profile.sh y
# scripts/apply-default-role.sh. No verifica el resultado: para eso se ejecuta
# después scripts/check-realm.sh. No admite argumentos ni opciones y se detiene
# al primer fallo. Los dos scripts individuales siguen disponibles para
# ejecutarlos por separado al depurar.

set -euo pipefail

if [[ "$#" -ne 0 ]]; then
  echo "ERROR: este script no admite argumentos ni opciones (incluido --force)" >&2
  echo "Uso: scripts/apply-realm-config.sh" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== Perfil de usuario (ACO-012 P17) =="
"${script_dir}/apply-user-profile.sh"

echo "== Rol por defecto (ACO-012 P18) =="
"${script_dir}/apply-default-role.sh"

echo "OK: configuración post-importación del realm acompas aplicada"
