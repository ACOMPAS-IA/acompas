# ADR-011 — Autenticación y autorización
Estado: aprobado  
Sustituido por: —  
Origen: Plan de Proyecto  
Relacionados: ADR-001, ADR-009  

## Contexto
ACOMPAS trata documentación clínica y datos de pacientes, por lo que debe controlar el acceso desde el inicio.
El sistema distingue dos tipos de usuario: paciente y administrador.

## Decisión
Keycloak self-hosted es el proveedor de identidad y control de acceso, integrado mediante OpenID Connect sobre OAuth 2.0.
- El 2FA es obligatorio y lo gestiona Keycloak.
- Las peticiones al backend usan un JWT firmado y con expiración; el backend valida el token y aplica la autorización.
- Roles: paciente y administrador. Un paciente solo accede a sus recursos.
- Las credenciales no se almacenan en la base de datos de ACOMPAS ni se implementa un sistema de autenticación paralelo.
- Durante el piloto, el alta se limita a la lista blanca de emails autorizados por ACANPAN (ver ADR-009).

## Alternativas consideradas
- Autenticación propia en el backend, con credenciales en la base de datos de ACOMPAS: descartada por el riesgo y el esfuerzo de mantener un sistema de autenticación seguro con 2FA.
- Proveedor de identidad gestionado en la nube: descartado porque los datos de identidad de los pacientes quedarían en un tercero fuera del servidor propio; Keycloak self-hosted ya forma parte del stack.

## Consecuencias
- Keycloak se convierte en un componente crítico: su configuración, seguridad y disponibilidad afectan al acceso de los usuarios.
- Una configuración incorrecta de Keycloak o una validación incompleta del JWT en el backend puede permitir accesos indebidos.
- La identidad interna del paciente se resuelve conforme a ADR-001.

## Fuera de esta decisión
- Valores de expiración de tokens y claims del JWT.
- Flujo OIDC concreto y configuración de clientes y realms.
- Política de contraseñas y recuperación de cuenta.
- Backups de Keycloak e infraestructura donde se despliega.

## Documentos afectados
Arquitectura del Sistema.
