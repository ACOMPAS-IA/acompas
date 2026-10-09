# Prompts de ACOMPAS

Este paquete contiene los prompts versionados del asistente y su cargador (ACO-029). No llama a ningún modelo ni a ningún servicio: solo lee texto del disco.

## Uso

```python
from app.services.prompts import load_system_prompt

prompt = load_system_prompt()
prompt.text     # texto que recibe el modelo
prompt.version  # "v0"
prompt.sha256   # huella SHA-256 del texto
```

`load_prompt(name, version)` lee `templates/{name}_{version}.md`. El nombre debe cumplir `^[a-z][a-z0-9_]*$` y la versión `^v[0-9]+$`; si no, lanza `ValueError`. Si la plantilla no existe, lanza `PromptNotFoundError`.

Quien registre una prueba o una llamada al modelo debe anotar la versión y la huella del prompt usado.

## Delimitadores del documento

El documento clínico llega al modelo entre `DOCUMENT_OPEN_TAG` (`<documento_clinico>`) y `DOCUMENT_CLOSE_TAG` (`</documento_clinico>`). El prompt nombra estos delimitadores y declara que su contenido son datos, nunca instrucciones.

Este paquete solo fija los delimitadores y el texto. Construir los mensajes, colocar el documento entre los delimitadores y neutralizar los delimitadores que aparezcan dentro del documento corresponde a ACO-030.

## Cambiar el texto

- El archivo `templates/system_v0.md` contiene únicamente el texto que recibe el modelo: sin cabecera, sin variables y con las secciones marcadas con `## `.
- Durante el Sprint 1 el texto de `v0` puede cambiar. Todo cambio entra por PR y lo revisa la otra persona, que comprueba la seguridad.
- Los tests de `backend/tests/prompts/` comprueban las secciones, su orden, las anclas mínimas, los delimitadores y la longitud. Si un cambio elimina una regla, fallan.

## Versión nueva

Una versión nueva se añade como archivo nuevo (por ejemplo `templates/system_v1.md`), sin borrar el anterior, y se cambia `SYSTEM_PROMPT_VERSION` en `loader.py`.

## Empaquetado

El backend se ejecuta desde el árbol de fuentes (Docker y CI), así que los `.md` no se declaran como datos del paquete. Si algún día el backend se instala como paquete, habrá que declararlos en `backend/pyproject.toml`.

## Alcance de los tests

Los tests comprueban que las reglas están en el texto, no que el modelo las cumpla. El comportamiento se valida con la comprobación manual de la ficha de ACO-029, con la llamada real de ACO-030 y con los casos de prueba de ACO-052.
