# ADR-003 — Anonimización en tres niveles; el Nivel 3 es la revisión manual del paciente
Estado: aprobado  
Sustituido por: —  
Origen: Plan de Proyecto  
Relacionados: ADR-004, ADR-005, ADR-008  

## Contexto
ACOMPAS trata documentación clínica y la anonimiza en tres niveles antes de que entre en el sistema. Inicialmente el Nivel 3 era una segunda pasada de Claude API como NER sobre el texto pseudoanonimizado.

## Decisión
La anonimización se hace en tres niveles:
- Nivel 1: Presidio con etiquetado automático y validación automática por umbral de confianza; si la confianza es baja, el documento se retiene y no se carga. Cumple el requisito legal mínimo de pseudoanonimización.
- Nivel 2: validación automática reforzada de entidades, sobre el texto que extrae el OCR local (ADR-004).
- Nivel 3: revisión manual del paciente. Revisa el documento ya anonimizado por los Niveles 1 y 2 y puede marcar lo que se haya escapado, como red de seguridad adicional.

## Alternativas consideradas
- Segunda pasada de Claude API como NER (Nivel 3 inicial): descartada.

## Consecuencias
- Ya no hay llamada adicional a Claude API sobre el texto pseudoanonimizado.
- El paciente participa en la revisión final del documento anonimizado.
- El Nivel 2 depende del OCR local definido en ADR-004.

## Fuera de esta decisión
- Valor del umbral de confianza, objetivo de cobertura y reglas concretas de Presidio.

## Documentos afectados
Arquitectura del Sistema.
