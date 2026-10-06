# ADR-005 — El documento original no se persiste
Estado: aprobado  
Sustituido por: —  
Origen: Plan de Proyecto  
Relacionados: ADR-003, ADR-004, ADR-012  

## Contexto
ACOMPAS recibe documentación clínica de pacientes que contiene datos identificativos.
Conservar el original ampliaría la exposición de esos datos.

## Decisión
El documento original no se persiste: se procesa en memoria o en un volumen efímero hasta generar la versión anonimizada, que es lo único que se guarda.

## Alternativas consideradas
- Persistir el original cifrado para poder reprocesarlo si mejora la anonimización: descartada porque mantiene almacenados datos identificativos y exige custodia y borrado adicionales.
- Conservar el original durante un plazo limitado y borrarlo después: descartada porque durante ese plazo la exposición es la misma y añade un borrado programado que verificar.

## Consecuencias
- Solo la versión anonimizada queda almacenada; los datos derivados del original que se conservan (nombre genérico y hash del fichero) los define ADR-012.
- Una vez procesado, el documento original no puede recuperarse desde ACOMPAS.

## Documentos afectados
Arquitectura del Sistema.
