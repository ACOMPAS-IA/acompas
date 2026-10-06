# ADR-002 — Eliminación del rol de mediador: uso directo por pacientes desde el inicio
Estado: aprobado  
Sustituido por: —  
Origen: Decisión de ACANPAN, 10 de septiembre de 2026  
Relacionados: ADR-006, ADR-011  

## Contexto
El diseño previo contemplaba un mediador entre ACOMPAS y el paciente.
ACANPAN decidió el 10 de septiembre de 2026 eliminar ese rol.

## Decisión
Se elimina el rol de mediador: los pacientes usan ACOMPAS directamente desde el inicio. Los roles son paciente y administrador.

## Alternativas consideradas
- Mantener el modelo con mediador: descartado por decisión de ACANPAN.

## Consecuencias
- Los controles de uso oncológico (clasificador de intención, control de gasto y monitorización avanzada) pasan a ser necesarios desde el inicio, no para una fase futura.
- Desaparece el flujo del mediador; el paciente se autentica directamente.

## Documentos afectados
Plan de Proyecto, Arquitectura del Sistema.
