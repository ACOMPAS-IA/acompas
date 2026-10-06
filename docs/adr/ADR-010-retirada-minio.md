# ADR-010 — Retirada de MinIO como recomendación de almacenamiento
Estado: aprobado  
Sustituido por: —  
Origen: Plan de Proyecto  
Relacionados: ADR-007  

## Contexto
MinIO era la recomendación de almacenamiento. Su repositorio está archivado desde abril de 2026 y ya no recibe parches de seguridad.

## Decisión
Se retira MinIO como recomendación de almacenamiento. Primero se evalúa si hace falta almacenamiento de objetos; si se necesita API S3, se valoran Garage o SeaweedFS.

## Alternativas consideradas
- MinIO: retirada (repositorio archivado, sin parches de seguridad).
- Garage y SeaweedFS: alternativas a valorar si se necesita API S3.

## Consecuencias
- No se recomienda MinIO para ningún almacenamiento de ACOMPAS.
- La necesidad de almacenamiento de objetos se evalúa antes de elegir tecnología.

## Fuera de esta decisión
- La elección final de almacenamiento (pendiente).

## Documentos afectados
Arquitectura del Sistema.
