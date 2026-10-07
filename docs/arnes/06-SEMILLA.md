# 06 — SEMILLA

> Pieza del arnés de ACOMPAS. Es una capa derivada: no decide, no es fuente de verdad y se regenera, no se edita a mano. Ante cualquier conflicto prevalece la fuente oficial. Las versiones exactas de las fuentes constan en `docs/arnes/MANIFIESTO.md`.

## Objetivo y alcance

Datos sintéticos y configuración inicial que pueden cargarse de forma controlada. Solo incluye datos que tienen fuente o un procedimiento de revisión humana. Los datos clínicos de prueba son siempre sintéticos.

## Qué no contiene

- Datos reales de pacientes, ni fragmentos de documentos reales, ni siquiera anonimizados.
- Secretos, contraseñas ni API keys (R-24).
- Valores de catálogos o de configuración que ninguna fuente fija: aparecen como cuestión abierta.

## Fuentes

- **Normativas:** Plan de Proyecto (§2); Arquitectura del Sistema (§6, §11); ADR-008, ADR-009 y ADR-011.
- **Derivadas:** Fichas ACO de docs/aco/: ACO-051 (corpus sintético), ACO-012 (realm) y ACO-015 (lista blanca).

## 1. Principio

Ningún entorno contiene datos reales de pacientes hasta que estén operativos la anonimización, el derecho al olvido básico y el registro de auditoría. Eso incluye desarrollo y pruebas. *(ADR-008; Arquitectura §11; Plan de Proyecto §2)*

## 2. Corpus clínico sintético (ACO-051)

*(ACO-051, criterios confirmados en la revisión de su PR)*

- **Ubicación:** `backend/tests/synthetic_data/`, con `README.md`, `expected_entities.json`, `__init__.py` (funciones de carga `load_document`, `load_manifest` y `count_occurrences`, solo con la biblioteca estándar) y `documents/` con tres textos: `informe_patologia_01.txt`, `analitica_01.txt` y `carta_oncologia_01.txt`.
- **Formato:** texto plano UTF-8, en español de España, de 250 a 700 palabras por documento. Los tres corresponden al mismo paciente ficticio con adenocarcinoma de páncreas, e incluyen diagnóstico, estadio, al menos un marcador con su valor y un plan de tratamiento.
- **Manifiesto:** `{"documents": [{"file", "type", "entities": [{"text", "category", "count"}]}]}`. `count` cuenta coincidencias de palabra completa, sensibles a mayúsculas, con `(?<!\w)` y `(?!\w)` (aclaración B2). El manifiesto es la referencia del criterio de la demo «no se escapa ninguna entidad de los casos definidos».
- **Categorías mínimas:** `PERSON`, `DATE_TIME`, `PHONE_NUMBER`, `EMAIL_ADDRESS`, `ES_DNI`, `ES_HISTORIA_CLINICA`, `ID_ASEGURAMIENTO`, `CALLE`, `HOSPITAL`, `TERRITORIO`. Además se colocan `ID_TITULACION_PERSONAL_SANITARIO`, `ID_CONTACTO_ASISTENCIAL`, `AGE` y `SEXO` (B3). Las categorías válidas son los tipos de entidad del analizador de anonimización (B1).
- **Reglas para que ningún dato sea real** *(ACO-051 §8)*:
  - nombres, apellidos, hospital, localidad y calle inventados; la provincia puede ser real (B5);
  - correos solo en `example.com`, `example.org` o `example.net`;
  - DNI solo `12345678Z`, `87654321X` o `00000000T`;
  - teléfonos con un patrón evidente (p. ej. `600 123 456`);
  - números de historia, de tarjeta sanitaria y de colegiado inventados;
  - contenido clínico escrito desde cero, sin revisión oncológica (el README lo declara).
- **Qué no incluye:** PDF ni imágenes (S2), ni documentos con instrucciones incrustadas para prompt injection (eso es de ACO-052).

Cualquier dato sintético nuevo que creen otros ACO sigue estas mismas reglas. *(Inferencia de ADR-008 y ACO-051. Es lo mínimo compatible con las fuentes, no una regla nueva.)*

## 3. Configuración inicial

| Elemento | Qué está definido | Fuente |
|---|---|---|
| Realm de Keycloak | Realm de ACOMPAS creado de forma **reproducible**, con la configuración base para clientes y usuarios del piloto, y documentado. 2FA obligatorio. | ACO-012; ADR-011 |
| Lista blanca | La gestiona **manualmente el administrador**, se guarda en la base de datos de ACOMPAS y contiene emails autorizados por ACANPAN, sin referencia al UUID. | ADR-009; Arquitectura §11 |
| Glosario | **Sin semilla inicial validada.** El LLM lo construye progresivamente y cada entrada nueva queda pendiente de validación. | Arquitectura §6 (D6) |
| Usuarios de prueba | Deben poder probarse un usuario autorizado y uno no autorizado. | ACO-015 |

## Cuestiones abiertas

| Cuestión | Fuente |
|---|---|
| Emails de la lista blanca y usuarios de prueba en desarrollo: ninguna fuente fija sus valores. Por coherencia con ACO-051, lo esperable son dominios reservados (`example.*`), pero es una **inferencia**: debe confirmarse en la ficha del ACO. | ACO-015; ADR-008 |
| Catálogos iniciales (TIPO_DOCUMENTO, TIPO_ETIQUETA): no hay valores semilla aprobados. Los ejemplos están en 02-DOMINIO. | Modelo E/R; ADR-012 |
| Valores iniciales de crédito (topes diario y mensual) por paciente. | Plan de Trabajo §9 (regla de cálculo del crédito) |
| Flujo OIDC, clientes y política de contraseñas del realm. | ADR-011 (Fuera de esta decisión) |
| Cómo se comprueba la lista blanca y cómo se conecta con el login. | ADR-009 (Fuera de esta decisión) |
| Casos de prueba conversacionales y de prompt injection (contenido). | ACO-052 (criterios pendientes de revisión) |
