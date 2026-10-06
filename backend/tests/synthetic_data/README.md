# Datos sintéticos para demo (ACO-051)

> **Todo el contenido de esta carpeta es ficticio.** No hay ningún paciente, profesional, familiar, hospital ni dirección reales, y los documentos se han escrito desde cero, sin partir de ningún documento real.

Esta carpeta contiene tres documentos clínicos oncológicos sintéticos, en español y en texto plano UTF-8. Los tres son de la misma paciente ficticia, Rosario Albendea Quintanar, con un adenocarcinoma de páncreas:

| Archivo | Tipo |
| --- | --- |
| `documents/informe_patologia_01.txt` | Informe de anatomía patológica |
| `documents/analitica_01.txt` | Analítica con marcadores tumorales |
| `documents/carta_oncologia_01.txt` | Informe de consulta de oncología con el plan de tratamiento |

Los datos identificativos se han colocado a propósito y están listados en `expected_entities.json`. Ficha: [`docs/acos/ACO-051.md`](../../../docs/acos/ACO-051.md).

## Reglas para que ningún dato sea real

- Los nombres, el hospital (`Hospital Universitario Monteluz`), la localidad (`Villaserena`) y la calle son inventados. La provincia (`Valladolid`) es real.
- Los correos usan solo los dominios reservados `example.com`, `example.org` y `example.net`.
- El único DNI es `12345678Z`. La lista permitida es `12345678Z`, `87654321X` y `00000000T`.
- Los teléfonos siguen patrones evidentes: `600 123 456` y `900 000 000`.
- Los números de historia clínica, tarjeta sanitaria, petición y colegiado son inventados.

## Contenido clínico

El contenido clínico es verosímil y coherente entre los tres documentos, pero **no pretende ser exacto ni completo desde el punto de vista médico, y no ha sido revisado por un oncólogo**. Se usa para probar la anonimización y para tener de qué conversar en la demo: diagnóstico, estadio, marcadores tumorales con sus valores y plan de tratamiento.

## Formato del manifiesto

`expected_entities.json` es un objeto con una lista `documents`. Cada elemento tiene:

- `file`: nombre del archivo dentro de `documents/`;
- `type`: tipo de documento;
- `entities`: lista de datos identificativos colocados en ese documento.

Cada entidad tiene:

- `text`: el texto exacto tal como aparece en el documento;
- `category`: un tipo de entidad de los de `backend/app/services/anonymization/analyzer.py`, es decir, de `DEFAULT_ENTITIES` o de los valores de `MEDDOCAN_ENTITY_MAPPING`;
- `count`: el número de apariciones de `text` en ese documento.

```json
{"text": "Albendea Quintanar", "category": "PERSON", "count": 2}
```

### Cómo se cuenta `count`

Cada `text` se busca como palabra completa y distinguiendo mayúsculas. La búsqueda usa la expresión `(?<!\w)<texto escapado>(?!\w)`, en lugar de `\b`, para que funcione también con textos que empiezan o acaban en un signo. Es lo que hace `count_occurrences`.

Una entidad puede estar contenida en otra, y cada recuento es independiente. Por ejemplo, en `carta_oncologia_01.txt`:

- `Rosario Albendea Quintanar` aparece 1 vez;
- `Albendea Quintanar` aparece 2 veces: la que va dentro del nombre completo y la mención parcial «Sra. Albendea Quintanar».

La mención solo con apellidos está puesta a propósito, porque es un caso típico de fuga en anonimización. En cambio, `ALBENDEA QUINTANAR, ROSARIO` (en mayúsculas) es una entidad distinta y no cuenta para `Albendea Quintanar`.

## Uso desde otros tests

```python
from tests.synthetic_data import count_occurrences, load_document, load_manifest

text = load_document("carta_oncologia_01.txt")
manifest = load_manifest()
```

Las funciones solo usan la biblioteca estándar: no necesitan red, modelos ni el analizador.

Los tests de esta carpeta se ejecutan así:

```
docker compose exec backend pytest tests/synthetic_data -q
```
