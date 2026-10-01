# ACOMPAS — Agent Development Rules

## 1. Propósito

Este archivo define las reglas que debe seguir cualquier agente de IA que participe en el desarrollo de ACOMPAS.

No sustituye al Plan de Proyecto, al Plan de Trabajo, al Documento Operativo ni a las fichas de los ACO.

El agente debe utilizar esos documentos como contexto del proyecto y esta guía como reglas de ejecución.

## 2. Fuente de verdad

Antes de actuar, el agente debe consultar:

1. `AGENTS.md`.
2. La ficha del ACO asignado.
3. El Documento Operativo del Sprint correspondiente.
4. El Plan de Trabajo.
5. El Plan de Proyecto.
6. La documentación de arquitectura y ADR aplicables.
7. El código existente.

Si existe una contradicción entre documentos, el agente no decide por su cuenta: declara `BLOQUEO` y explica qué decisión falta.

## 3. Regla fundamental

El agente ejecuta un ACO concreto; no redefine el proyecto.

No amplía el alcance por iniciativa propia, no modifica decisiones arquitectónicas sin autorización y no inventa requisitos.

Si necesita una decisión no especificada para continuar: `BLOQUEO`.

## 4. Alcance del trabajo

Cada ejecución debe estar asociada a un ACO concreto y conocer, como mínimo:

- objetivo;
- responsable;
- dependencias;
- alcance incluido;
- alcance excluido;
- criterios de aceptación;
- tests esperados;
- componentes que puede modificar.

Si esta información no está suficientemente definida, no debe empezar a implementar.

## 5. Git

Está prohibido:

- trabajar directamente sobre `main`;
- hacer push directamente a `main`;
- modificar ramas de otra persona sin autorización;
- mezclar cambios de otros ACOs en el trabajo actual.

El flujo normal es:

`ACO → rama feature/ACO-XXX-descripcion → implementación → tests → commit → push → PR → revisión → CI → merge`.

## 6. Dependencias

El agente debe respetar las dependencias declaradas por el ACO.

No debe implementar una dependencia futura ni incorporar una librería, servicio, modelo o infraestructura no contemplados.

Si necesita una dependencia no aprobada: `BLOQUEO — dependencia no aprobada`.

## 7. Arquitectura

Debe respetarse la arquitectura existente.

No se deben introducir por iniciativa propia:

- nuevos patrones arquitectónicos;
- nuevos servicios innecesarios;
- nuevas tecnologías;
- cambios de contratos entre componentes;
- cambios del modelo de datos aprobado;
- sustituciones de tecnologías existentes.

Una modificación arquitectónica requiere decisión humana y, cuando corresponda, ADR.

## 8. Seguridad y privacidad

ACOMPAS trabaja con información clínica.

Está prohibido utilizar datos reales de pacientes en desarrollo, pruebas o demostraciones de Sprint 1.

Nunca se deben:

- introducir secretos en el código;
- escribir API keys en el repositorio;
- registrar información clínica sensible innecesariamente;
- persistir documentos originales cuando el diseño indique que no deben persistirse;
- desactivar controles de seguridad para facilitar una prueba.

Ante una duda relevante de seguridad o privacidad: `BLOQUEO`.

## 9. Datos de prueba

Las pruebas deben utilizar datos sintéticos o expresamente autorizados.

Los documentos clínicos originales no deben aparecer en logs, mensajes de error, fixtures, commits, documentación, capturas ni archivos temporales persistentes.

Cuando una regla de privacidad sea verificable, debe convertirse en una comprobación automatizada cuando resulte razonable.

## 10. Dependencias externas

Antes de introducir una dependencia nueva, comprobar que:

1. está contemplada en el ACO;
2. es compatible con la arquitectura aprobada;
3. no contradice decisiones existentes.

Si no se cumple alguna condición, detenerse y solicitar decisión.

## 11. Tests

Todo comportamiento verificable debe tener una prueba adecuada.

Antes de finalizar el trabajo, el agente debe:

1. ejecutar los tests relevantes;
2. comprobar que pasan;
3. ejecutar las comprobaciones necesarias del proyecto;
4. informar de cualquier fallo que no pueda resolver dentro del alcance.

El agente no puede considerar terminado un ACO solo porque el código parezca correcto.

## 12. Cambios fuera de alcance

Si aparece un problema que pertenece a otro ACO, no debe implementarlo como parte del ACO actual salvo autorización explícita.

Debe señalarlo como:

`FUERA DE ALCANCE — requiere ACO-XXX`.

## 13. Documentación

Una decisión nueva no debe quedar convertida en decisión permanente únicamente mediante un comentario de código.

Si una decisión aprobada modifica el alcance o los criterios de un ACO, debe actualizarse su ficha.

## 14. Modo de ejecución

Cuando se solicite ejecutar un ACO, trabajar en tres fases:

### PLAN

- leer `AGENTS.md`;
- leer la ficha del ACO;
- comprobar dependencias;
- inspeccionar el código existente;
- identificar cambios necesarios;
- identificar riesgos y decisiones no especificadas.

Si todo está definido, presentar el plan antes de modificar código cuando el flujo de trabajo lo requiera.

### BUILD

Implementar exclusivamente el alcance aprobado.

### TEST

Ejecutar las pruebas y comprobaciones correspondientes e informar de resultados, incidencias y bloqueos.

## 15. Regla de bloqueo

El agente debe detenerse cuando:

- falte información necesaria;
- exista una contradicción entre documentos;
- necesite tomar una decisión arquitectónica no definida;
- necesite introducir una dependencia no aprobada;
- exista una duda relevante de seguridad o privacidad;
- el trabajo requiera modificar otro ACO;
- no pueda cumplir los criterios de aceptación definidos.

**Ante una decisión no especificada, bloquear. No inventar.**

## 16. Responsabilidad humana

El agente puede analizar, proponer, implementar, ejecutar tests y preparar un PR.

La aceptación del cambio corresponde a las personas responsables del proyecto.

Todo código generado por un agente está sujeto a revisión humana.

## 17. Definition of Done

Un ACO ejecutado por un agente no se considera terminado hasta que:

- el trabajo está en su rama correspondiente;
- cumple el alcance de la ficha;
- los tests relevantes pasan;
- no contiene datos reales de pacientes;
- respeta seguridad y privacidad;
- el PR está abierto;
- CI está verde;
- la revisión humana se ha realizado;
- las observaciones bloqueantes se han resuelto;
- el PR ha sido aprobado y fusionado.
