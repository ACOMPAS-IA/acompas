# ADR-001 — Keycloak es el único custodio de la correspondencia email↔UUID
Estado: aprobado  
Sustituido por: —  
Origen: Plan de Proyecto  
Relacionados: ADR-002, ADR-009  

## Contexto
El diseño previo asignaba a cada paciente un UUID interno y ACANPAN custodiaba la correspondencia con su identidad real en un registro externo al sistema.
Esto suponía una carga operativa y una responsabilidad de custodia para ACANPAN. Keycloak ya forma parte del stack de ACOMPAS.

## Decisión
Keycloak es el único custodio de la correspondencia email↔UUID. El paciente se autentica en Keycloak, que resuelve o crea su UUID; ACOMPAS solo opera con ese UUID y nunca almacena el email. ACANPAN no custodia la correspondencia ni se asignan UUID manualmente.
- Keycloak: gestiona la identidad y la autenticación, conoce el email y mantiene la correspondencia email↔UUID.
- ACOMPAS: identifica al paciente solo mediante UUID y no almacena el email.
- Durante el piloto, el alta se limita a la lista blanca de emails autorizados por ACANPAN (ver ADR-009).

## Alternativas consideradas
- Que ACANPAN custodie la correspondencia en un registro externo: descartada por la carga operativa que supone para ACANPAN.

## Consecuencias
- El derecho al olvido incluye borrar los datos asociados al UUID en ACOMPAS y la cuenta del paciente en Keycloak.
- Limitación conocida: sin el email del paciente, su UUID solo puede recuperarse consultando directamente a Keycloak con permisos de administrador, porque ACOMPAS no lo almacena.
- No cambia el modelo de datos: la entidad de paciente conserva solo el UUID como identificador.

## Fuera de esta decisión
- Procedimiento detallado de borrado y de verificación del borrado.
- Uso de la Admin API de Keycloak y cómo se autentican sus llamadas.
- Caso de un paciente con dos emails distintos en momentos diferentes.

## Documentos afectados
Arquitectura del Sistema, Modelo E/R.
