# ADR-006 — LLM gateway como paso obligatorio de toda llamada a Claude API
Estado: aprobado  
Sustituido por: —  
Origen: Plan de Proyecto  
Relacionados: ADR-002  

## Contexto
ACOMPAS usa Claude API en un entorno de uso oncológico directo por pacientes.
Se necesita un punto único donde controlar el gasto y clasificar la intención de las peticiones.

## Decisión
Existe un módulo LLM gateway por el que pasa toda llamada a Claude API. Integra el control de gasto (tope diario y mensual, crédito acumulado, desbloqueo manual, modo pruebas y marcado individual) y el clasificador de intención.

## Alternativas consideradas
- Llamadas directas a Claude API desde cada módulo, con el control de gasto y la clasificación repartidos: descartada porque los controles no serían uniformes y una llamada podría saltárselos.
- Proxy LLM de terceros: descartada porque el modelo de crédito por paciente y el clasificador de intención son lógica propia de ACOMPAS y se añadiría un componente externo en la ruta de datos.

## Consecuencias
- Ninguna llamada a Claude API puede hacerse al margen del gateway.
- El control de gasto y el clasificador de intención se aplican de forma uniforme en un único punto.

## Documentos afectados
Arquitectura del Sistema.
