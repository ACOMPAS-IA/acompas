# ADR-007 — Una sola base de datos: PostgreSQL + pgvector
Estado: aprobado  
Sustituido por: —  
Origen: Plan de Proyecto  
Relacionados: ADR-001  

## Contexto
ACOMPAS necesita almacenar datos estructurados y los vectores del RAG.
Se quiere evitar que se introduzca una segunda base de datos o un motor vectorial independiente sin una decisión explícita.

## Decisión
PostgreSQL es la única base de datos de aplicación, con pgvector para los vectores del RAG, SQLAlchemy como capa de acceso y Alembic para las migraciones. Los vectores conservan trazabilidad hacia su fuente.

## Alternativas consideradas
- Una base de datos vectorial independiente: descartada.

## Consecuencias
- Menor complejidad operativa y desarrollo local más sencillo.
- PostgreSQL pasa a ser un componente crítico.
- El rendimiento de pgvector debe verificarse si el corpus crece; una solución especializada podría ser más eficiente a mayor escala.
- Añadir otra base de datos requerirá una decisión explícita.

## Fuera de esta decisión
- Modelo de embeddings, dimensionalidad, chunking, índice, parámetros y umbrales de búsqueda.
- Modelo de datos relacional, almacenamiento de objetos y copias de seguridad.

## Documentos afectados
Arquitectura del Sistema, Modelo E/R.
