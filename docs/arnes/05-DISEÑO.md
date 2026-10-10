# 05 — DISEÑO

> Pieza del arnés de ACOMPAS. Es una capa derivada: no decide, no es fuente de verdad y se regenera, no se edita a mano. Ante cualquier conflicto prevalece la fuente oficial. Las versiones exactas de las fuentes constan en `docs/arnes/MANIFIESTO.md`.

## Objetivo y alcance

Traduce la Arquitectura del Sistema a módulos con responsabilidades y fronteras implementables. El agente **no elige** patrones ni tecnologías: usa los que aquí se indican, y lo que no esté indicado es una cuestión abierta o requiere ADR (03-REGLAS R-32, R-38, R-40).

## Qué no contiene

- Contratos concretos entre módulos (formatos, endpoints): están en 07-INTERCAMBIO.
- Estructura de ficheros del repositorio: la fija cada Ficha ACO (ver 08-PLAN).
- Infraestructura de producción (VPS), que queda fuera del Sprint 1.

## Fuentes

- **Normativas:** Arquitectura del Sistema (§3, §4, §5, §6, §7, §8, §9, §10, §11, §13, §14); Plan de Proyecto (§2); ADR-001, ADR-003, ADR-004, ADR-005, ADR-006, ADR-007, ADR-009, ADR-010, ADR-011, ADR-012 y ADR-013.
- **Derivadas:** Wireframes MVP (componentes de interfaz); Modelo E/R (persistencia).

## 1. Stack (cerrado)

*(Arquitectura §10; Plan de Proyecto §2)*

| Capa | Tecnología |
|---|---|
| Backend | Python + FastAPI |
| ORM y migraciones | SQLAlchemy + Alembic |
| Base de datos | PostgreSQL + pgvector (única) |
| Almacenamiento de objetos | **Por decidir** (PostgreSQL o volumen cifrado; Garage o SeaweedFS si hace falta API S3). Nunca MinIO. |
| LLM | Claude API (Anthropic), siempre a través del LLM gateway |
| Anonimización | Microsoft Presidio |
| OCR | Tesseract local; docTR o PaddleOCR si no rinde (S2) |
| Orquestación LLM y RAG | LlamaIndex |
| Embeddings | sentence-transformers, en local |
| Frontend | React |
| Autenticación | Keycloak self-hosted (OAuth2/OIDC, JWT, 2FA) |
| Entorno de desarrollo | Docker Compose; nadie depende del VPS (Arquitectura §13) |

## 2. Módulos y responsabilidades

| Módulo | Responsabilidad | No hace | Fuente |
|---|---|---|---|
| **Identidad (Keycloak)** | Autenticación OIDC con 2FA; emite el JWT; custodia la correspondencia email↔UUID; resuelve o crea el UUID solo para emails autorizados. | No lo sustituye ningún sistema paralelo. ACOMPAS no guarda credenciales. | ADR-001, ADR-011; Arquitectura §11 |
| **Backend API (FastAPI)** | Valida el JWT en cada petición protegida y aplica la autorización por rol y por propiedad del recurso; expone las APIs internas; comprueba la lista blanca. | No almacena el email del paciente. | ADR-011, ADR-009; Arquitectura §3 |
| **Frontend (React)** | Login, layout, cliente de API centralizado con autenticación, subida de documento, conversación con disclaimer. | No accede a la API key del LLM ni llama al LLM directamente. | Arquitectura §3, §11; Wireframes |
| **Anonimización** | Pipeline: extracción de texto (si el texto extraído está vacío, el documento es ilegible y no se procesa) → Presidio Analyzer (detección de las categorías garantizadas y sin garantía) → validación automática con dos umbrales configurables: el de hallazgo descarta el ruido y el de documento decide si se carga o se retiene → Presidio Anonymizer (etiquetas numeradas por documento, por rol cuando se puede determinar y genérica de persona si no). El original solo existe en memoria o en un volumen efímero. Del documento retenido solo queda un registro de auditoría sin contenido ni nombre del fichero. | No persiste el original ni el resultado anonimizado de un documento retenido, no guarda valores originales, no deja el nombre del fichero original en logs ni temporales y no llama a Claude API. | ADR-003, ADR-005, ADR-012, ADR-013; Arquitectura §4, §11 |
| **LLM gateway** | Punto de paso obligatorio de toda llamada a Claude API. Mide tokens, aplica el modelo de crédito e integra el clasificador de intención. | No hay llamadas a Claude API al margen del gateway. | ADR-006; Arquitectura §8 |
| **Conversación** | Construye el contexto con el documento anonimizado del paciente (y, en sprints posteriores, el historial y el RAG), usa el prompt de sistema restringido y devuelve la respuesta con su origen y el disclaimer. | No recibe nunca el documento original. | Arquitectura §3, §6, §11 |
| **Persistencia (PostgreSQL + pgvector)** | Datos estructurados (Modelo E/R) y vectores del RAG, con trazabilidad hacia su fuente. | No hay una segunda base de datos. | ADR-007; Arquitectura §9 |
| **RAG** *(Fase 1.5; preparación en S2)* | Ingesta periódica de PubMed Central (cron), embeddings locales, índice HNSW en pgvector, curaduría por oncólogos, cita de fragmentos. | Ningún contenido del paciente sale para vectorizarse. | Arquitectura §5 |
| **Resumen y preferencias** *(S5)* | Genera el resumen aplicando PREFERENCIA_RESUMEN como reglas obligatorias; comprueba automáticamente que lo ocultado no aparece. | No edita el texto generado. | Arquitectura §7 |
| **Auditoría y derecho al olvido** *(S2)* | Registro de operaciones sensibles; borrado completo y verificable por UUID, incluido Keycloak. | — | Arquitectura §11; ADR-001 |

## 3. Implantación del Sprint 1

*(Arquitectura §14, fila S1)*

- **Pista A:** conversación básica. Claude responde sobre un informe oncológico sintético. El alcance del LLM gateway en el Sprint 1 está abierto (ver Cuestiones abiertas y 08-PLAN).
- **Pista B:** Nivel 1: Presidio básico, etiquetado automático y validación automática con umbral de hallazgo y umbral de documento. Qué se anonimiza y el tratamiento del documento retenido e ilegible están en 03-REGLAS (R-13, R-44…R-50).
- **Pista C:** Keycloak con 2FA y OAuth2/OIDC; JWT en todas las peticiones; registro validado contra la lista blanca.
- Persistencia del modelo de datos UUID, derecho al olvido y auditoría: Sprint 2.

Las áreas de trabajo y los responsables no son decisiones de diseño: se consultan en 08-PLAN.

## Cuestiones abiertas

| Cuestión | Fuente |
|---|---|
| Almacenamiento de objetos (si hace falta y con qué tecnología) | Arquitectura §16 nº 2; ADR-010 |
| Encaje mínimo y alcance del LLM gateway en el Sprint 1 | Plan de Trabajo §9; Documento Operativo §13; ACO-027 |
| Sprint del clasificador de intención | Arquitectura §16 nº 1 |
| Calendario y corpus del RAG en S3–S4 | Arquitectura §16 nº 6 |
| Modelo de embeddings, chunking e índice | ADR-007 (Fuera de esta decisión); Plan de Trabajo §9 |
| Motor de OCR definitivo (solo si Tesseract no rinde) | Plan de Trabajo §9 |
| Comprobación de que el documento es de tipo clínico antes de procesarlo | Arquitectura §16 nº 8 |
| Uso de la confianza del OCR para detectar documentos ilegibles, y si los umbrales cambian en los Niveles 2 y 3 o con documentos reales | Arquitectura §16 nº 9 |
| Diseño del Nivel 3: marcado y ocultación en el momento de la carga, almacenamiento temporal durante la revisión y marcado posterior; revisión obligatoria del documento retenido cuando exista | Arquitectura §16 nº 10 |
| Diseño del derecho al olvido y del registro de auditoría | Arquitectura §16 nº 3–4 |
| Flujo OIDC concreto, clientes y realms | ADR-011 (Fuera de esta decisión) |
| Modelo de Claude y política de versiones | Plan de Trabajo §9 |
