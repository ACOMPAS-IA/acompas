#!/usr/bin/env python3
"""Genera y comprueba el índice de ACO.

Lee docs/aco/sprints.toml y las fichas de docs/aco/ y escribe docs/indice.md.
Con --check compara el índice commiteado con el generado y no escribe nada.
"""

import argparse
import difflib
import re
import sys
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DIR_ACO = RAIZ / "docs" / "aco"
RUTA_TOML = DIR_ACO / "sprints.toml"
RUTA_INDICE = RAIZ / "docs" / "indice.md"

ESTADOS = ("pendiente", "en curso", "en revisión", "hecho", "traspasado")
CLAVES = {"id", "sprint", "estado", "issue", "casos_uso", "sin_ficha"}

RE_ID = re.compile(r"^\d{3}$")
RE_SPRINT = re.compile(r"^S[1-8]$")
RE_CASO = re.compile(r"^UC-\d{2}$")
RE_TITULO = re.compile(r"^# ACO-(\d{3}) — (.+)$")
RE_UC = re.compile(r"UC-\d{2}")


def relativa(ruta):
    return ruta.relative_to(RAIZ).as_posix()


def etiqueta(entrada, numero):
    ident = entrada.get("id") if isinstance(entrada, dict) else None
    if isinstance(ident, str):
        return f"ACO-{ident}"
    return f"entrada {numero}"


def cargar_entradas(errores):
    try:
        texto = RUTA_TOML.read_text(encoding="utf-8")
    except FileNotFoundError:
        errores.append(f"no existe {relativa(RUTA_TOML)}")
        return []

    try:
        datos = tomllib.loads(texto)
    except tomllib.TOMLDecodeError as exc:
        errores.append(f"{relativa(RUTA_TOML)}: TOML no válido: {exc}")
        return []

    for clave in sorted(set(datos) - {"aco"}):
        errores.append(f"{relativa(RUTA_TOML)}: clave desconocida en la raíz: {clave}")

    entradas = datos.get("aco")
    if not isinstance(entradas, list) or not entradas:
        errores.append(f"{relativa(RUTA_TOML)}: no hay entradas [[aco]]")
        return []

    return entradas


def validar_entradas(entradas, errores):
    por_id = {}

    for numero, entrada in enumerate(entradas, 1):
        if not isinstance(entrada, dict):
            errores.append(f"entrada {numero}: no es una tabla")
            continue

        nombre = etiqueta(entrada, numero)

        for clave in sorted(set(entrada) - CLAVES):
            errores.append(f"{nombre}: clave desconocida: {clave}")

        ident = entrada.get("id")
        if not isinstance(ident, str) or not RE_ID.match(ident):
            errores.append(f"{nombre}: «id» debe ser una cadena de tres dígitos")
        elif ident in por_id:
            errores.append(f"{nombre}: «id» duplicado")
        else:
            por_id[ident] = entrada

        estado = entrada.get("estado")
        if estado is None:
            errores.append(f"{nombre}: falta «estado»")
        elif not isinstance(estado, str) or estado not in ESTADOS:
            errores.append(
                f"{nombre}: estado no válido {estado!r}; "
                f"debe ser uno de: {', '.join(ESTADOS)}"
            )

        sprint = entrada.get("sprint")
        if sprint is not None and (
            not isinstance(sprint, str) or not RE_SPRINT.match(sprint)
        ):
            errores.append(f"{nombre}: «sprint» debe tener la forma S1 a S8")

        issue = entrada.get("issue")
        if issue is not None and (type(issue) is not int or issue < 1):
            errores.append(f"{nombre}: «issue» debe ser un entero positivo")

        casos = entrada.get("casos_uso")
        if casos is not None and (
            not isinstance(casos, list)
            or any(not isinstance(caso, str) or not RE_CASO.match(caso) for caso in casos)
        ):
            errores.append(f"{nombre}: «casos_uso» debe ser una lista de UC-NN")

        sin_ficha = entrada.get("sin_ficha")
        if sin_ficha is not None and (
            not isinstance(sin_ficha, str) or not sin_ficha.strip()
        ):
            errores.append(f"{nombre}: «sin_ficha» debe ser un motivo no vacío")

    orden = [
        entrada["id"]
        for entrada in entradas
        if isinstance(entrada, dict) and isinstance(entrada.get("id"), str)
    ]
    if (
        len(orden) == len(entradas)
        and len(set(orden)) == len(orden)
        and orden != sorted(orden)
    ):
        errores.append(
            f"{relativa(RUTA_TOML)}: las entradas no están ordenadas por «id»"
        )

    return por_id


def leer_titulos(por_id, fichas, errores):
    titulos = {}

    for ident in sorted(por_id):
        ruta = fichas.get(ident)
        if ruta is None:
            continue

        lineas = ruta.read_text(encoding="utf-8").splitlines()
        primera = lineas[0] if lineas else ""
        coincidencia = RE_TITULO.match(primera)
        if not coincidencia:
            errores.append(
                f"{relativa(ruta)}: la primera línea no tiene la forma "
                "«# ACO-NNN — Título»"
            )
            continue
        if coincidencia.group(1) != ident:
            errores.append(
                f"{relativa(ruta)}: el encabezado dice ACO-{coincidencia.group(1)} "
                f"y el fichero es ACO-{ident}"
            )
            continue
        titulos[ident] = coincidencia.group(2).strip()

    return titulos


def comprobar_fichas(por_id, fichas, errores):
    for ruta in fichas.values():
        ident = ruta.stem[4:]
        if ident not in por_id:
            errores.append(f"falta entrada para ACO-{ident}")

    for ident, entrada in sorted(por_id.items()):
        tiene_ficha = ident in fichas
        sin_ficha = entrada.get("sin_ficha")
        if not tiene_ficha and sin_ficha is None:
            errores.append(
                f"la entrada ACO-{ident} no tiene ficha "
                f"docs/aco/ACO-{ident}.md ni sin_ficha"
            )
        if tiene_ficha and sin_ficha is not None:
            errores.append(
                f"la entrada ACO-{ident} tiene ficha y también sin_ficha"
            )


def avisos_de_casos_uso(por_id, fichas):
    avisos = []

    for ident, entrada in sorted(por_id.items()):
        ruta = fichas.get(ident)
        if ruta is None:
            continue
        declarados = entrada.get("casos_uso") or []
        citados = sorted(set(RE_UC.findall(ruta.read_text(encoding="utf-8"))))
        for caso in citados:
            if caso not in declarados:
                avisos.append(
                    f"{relativa(ruta)}: cita {caso} y no está en casos_uso"
                )

    return avisos


def celda(texto):
    return str(texto).replace("|", r"\|")


def enlace_issue(numero):
    return (
        f"[#{numero}]"
        f"(https://github.com/ACOMPAS-IA/acompas/issues/{numero})"
    )


def fila(ident, entrada, titulo, fichas):
    casos = entrada.get("casos_uso") or []
    casos_uso = ", ".join(casos) if casos else "—"
    sprint = entrada.get("sprint") or "—"
    estado = entrada.get("estado") or "—"
    if ident in fichas:
        ficha = f"[ACO-{ident}](aco/ACO-{ident}.md)"
    else:
        ficha = "—"
    issue = entrada.get("issue")
    issue_enlace = enlace_issue(issue) if issue is not None else "—"

    return (
        f"| {celda(casos_uso)} | {ident} | {celda(titulo)} | {celda(sprint)} "
        f"| {celda(estado)} | {celda(ficha)} | {celda(issue_enlace)} |"
    )


def generar(por_id, titulos, fichas):
    lineas = [
        "# Índice de ACO",
        "",
        "> Generado por `scripts/indice.py` a partir de `docs/aco/sprints.toml` y",
        "> de las fichas de `docs/aco/`. No se edita a mano: se regenera con",
        "> `python scripts/indice.py`, y la CI comprueba que lo commiteado coincide",
        "> con lo generado.",
        "",
        "## Leyenda",
        "",
        "- **—** significa «no consta», no «no tiene».",
        "- **Estado:** `pendiente`, `en curso`, `en revisión`, `hecho` o",
        "  `traspasado`. No se compara con el estado de la Issue en GitHub.",
        "- **Caso de uso:** solo consta en los ACO que lo declaran en",
        "  `sprints.toml`; «—» no significa que el ACO no atienda ningún caso.",
        "",
        "## Tabla",
        "",
        "| Caso de uso | ACO | Título | Sprint | Estado | Ficha | Issue |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for ident in sorted(por_id):
        lineas.append(fila(ident, por_id[ident], titulos.get(ident, "—"), fichas))

    lineas += [
        "",
        "## Limitaciones",
        "",
        "- El Documento Operativo no está en el repositorio: si cambia sin que nadie",
        "  actualice `sprints.toml`, el índice no lo detecta.",
        "- El estado es el de `sprints.toml`; no se compara con el de la Issue en",
        "  GitHub.",
        "- Solo aparecen los ACO con ficha en `docs/aco/`. La lista completa vive en",
        "  el Documento Operativo, así que un ACO sin ficha y sin entrada no se",
        "  detecta.",
    ]

    sin_ficha = [
        (ident, entrada["sin_ficha"].strip())
        for ident, entrada in sorted(por_id.items())
        if ident not in fichas
    ]
    if sin_ficha:
        lineas += ["", "## Entradas sin ficha", ""]
        for ident, motivo in sin_ficha:
            lineas.append(f"- **ACO-{ident}:** {motivo}")

    return "\n".join(lineas) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="comprueba que docs/indice.md coincide con lo generado, sin escribirlo",
    )
    args = parser.parse_args()

    errores = []

    entradas = cargar_entradas(errores)
    por_id = validar_entradas(entradas, errores) if entradas else {}
    fichas = {ruta.stem[4:]: ruta for ruta in sorted(DIR_ACO.glob("ACO-*.md"))}
    comprobar_fichas(por_id, fichas, errores)
    titulos = leer_titulos(por_id, fichas, errores)

    if errores:
        for error in errores:
            print(f"error: {error}", file=sys.stderr)
        return 1

    for aviso in avisos_de_casos_uso(por_id, fichas):
        print(f"aviso: {aviso}", file=sys.stderr)

    generado = generar(por_id, titulos, fichas)
    generado_bytes = generado.encode("utf-8")

    if args.check:
        try:
            actual_bytes = RUTA_INDICE.read_bytes()
        except FileNotFoundError:
            print(
                f"error: no existe {relativa(RUTA_INDICE)}; "
                "ejecuta python scripts/indice.py",
                file=sys.stderr,
            )
            return 1

        if actual_bytes != generado_bytes:
            actual = actual_bytes.decode("utf-8", errors="replace")
            print(
                "error: docs/indice.md no coincide con lo generado; "
                "ejecuta python scripts/indice.py",
                file=sys.stderr,
            )
            sys.stdout.writelines(
                difflib.unified_diff(
                    actual.splitlines(keepends=True),
                    generado.splitlines(keepends=True),
                    fromfile="docs/indice.md (commiteado)",
                    tofile="docs/indice.md (generado)",
                )
            )
            return 1

        print("ok: docs/indice.md coincide con el TOML y las fichas")
        return 0

    RUTA_INDICE.write_bytes(generado_bytes)
    print(f"escrito: {relativa(RUTA_INDICE)} ({len(por_id)} entradas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
