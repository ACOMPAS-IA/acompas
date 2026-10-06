# ADR-009 — Lista blanca de emails autorizados durante el piloto
Estado: aprobado  
Sustituido por: —  
Origen: Plan de Proyecto  
Relacionados: ADR-001, ADR-011  

## Contexto
Durante el piloto el acceso a ACOMPAS debe limitarse a los pacientes que ACANPAN autorice.

## Decisión
Durante el piloto, el alta de usuarios se limita a emails autorizados por ACANPAN. La lista blanca se guarda en la base de datos de ACOMPAS y la gestiona manualmente el administrador; Keycloak solo resuelve o crea el UUID de un email autorizado. La restricción se retira al pasar a la fase de uso público.

## Alternativas consideradas
- Registro abierto desde el inicio: descartada porque el piloto se limita a pacientes que ACANPAN autoriza.

## Consecuencias
- La tabla de emails autorizados contiene emails previos al registro y no incluye referencia al UUID del paciente.
- El administrador mantiene la lista manualmente durante el piloto.
- La lista blanca no sustituye a la autenticación: el usuario debe además autenticarse en Keycloak.

## Fuera de esta decisión
- Cómo se comprueba la lista.
- Cómo se conecta esa comprobación con el login de Keycloak.

## Documentos afectados
Modelo E/R.
