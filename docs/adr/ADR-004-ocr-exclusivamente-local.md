# ADR-004 — OCR exclusivamente local
Estado: aprobado  
Sustituido por: —  
Origen: Plan de Proyecto  
Relacionados: ADR-003, ADR-005  

## Contexto
Los documentos que procesa ACOMPAS son documentación clínica de pacientes y requieren OCR.
Un OCR en la nube implicaría que el documento saliera del servidor propio.

## Decisión
El OCR se realiza exclusivamente en local con Tesseract; docTR o PaddleOCR son la alternativa si Tesseract no rinde. Ningún documento sale del servidor propio durante el OCR, y el documento original solo existe en memoria o en un volumen efímero.

## Alternativas consideradas
- AWS Textract: retirada.
- docTR o PaddleOCR: alternativa local si Tesseract no rinde.

## Consecuencias
- Ningún documento se envía a servicios externos de OCR.
- El rendimiento de Tesseract condiciona la elección; docTR o PaddleOCR quedan como plan alternativo.

## Documentos afectados
Arquitectura del Sistema.
