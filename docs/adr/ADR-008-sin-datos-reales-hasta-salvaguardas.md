# ADR-008 — Ningún dato real de paciente hasta que estén operativas las salvaguardas básicas
Estado: aprobado  
Sustituido por: —  
Origen: Plan de Proyecto  
Relacionados: ADR-003  

## Contexto
ACOMPAS trata documentación clínica de pacientes oncológicos.
Antes de manejar datos reales deben existir las salvaguardas que protegen a esos pacientes.

## Decisión
No se usa ningún dato real de paciente en ningún entorno hasta que estén operativos la anonimización, el derecho al olvido básico y el registro de auditoría.

## Alternativas consideradas
- Usar datos reales en desarrollo con acceso restringido al equipo: descartada porque no protege al paciente si falla la anonimización ni permite ejercer el derecho al olvido.
- Admitir datos reales en un único entorno aislado antes de tener las salvaguardas: descartada porque el aislamiento no sustituye a la anonimización, el derecho al olvido ni la auditoría.

## Consecuencias
- La anonimización, el derecho al olvido básico y el registro de auditoría se adelantan en el calendario para poder cumplir la regla cuanto antes.
- Hasta entonces, ningún entorno (incluidos los de desarrollo y pruebas) puede contener datos reales de pacientes.

## Documentos afectados
Plan de Proyecto, Arquitectura del Sistema.
