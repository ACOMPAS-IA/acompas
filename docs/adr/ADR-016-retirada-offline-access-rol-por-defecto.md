# ADR-016 — Retirada de `offline_access` del rol por defecto del realm

Estado: aprobado

Sustituido por: —

Origen: Decisión conjunta #99 (plazo 2–4 nov 2026; sin objeción registrada a la fecha de apertura de esta PR), con el apoyo de Luis del Olmo en el comentario de 3 nov. La PR de este ADR cierra #99; la implementación se sigue en #93.

Relacionados: ADR-011 (autenticación y autorización); ADR-017 (lista blanca y perfil de email; decisión en #102); ACO-012 (realm) y ACO-013 (cliente OIDC).

## Contexto

ACO-013 (PR #90, mergeada) cerró la parte del cliente: `acompas-frontend` declara `optionalClientScopes: []` y `scripts/check-realm.sh` comprueba que una petición con `scope=openid offline_access` se rechaza con `invalid_scope`.

Queda abierta la parte del realm. La importación limpia deja `default-roles-acompas` con `offline_access`, `uma_authorization`, `view-profile` y `manage-account`. Todos los usuarios del realm heredan el rol `offline_access`. Además, los clientes integrados de Keycloak (`account`, `admin-cli` y el resto) conservan `offline_access` entre sus scopes opcionales, y `admin-cli` tiene activada la concesión directa de contraseña.

En Keycloak, un token offline requiere el rol `offline_access` y que el cliente ofrezca el scope. Sin el rol, el scope queda inerte. El refresh token offline no caduca con la sesión SSO: por defecto dura 30 días de inactividad, y hasta 60 días si se activa Offline Session Max Limited. El rol no concede permisos de aplicación; el riesgo es la persistencia del token, no la autorización.

La concesión directa de `admin-cli` está bloqueada mientras el usuario tenga acciones pendientes (`CONFIGURE_TOTP`), pero no después. Un usuario que pida el scope contra uno de esos clientes podría obtener un refresh token que sobreviva al cierre de sesión.

El realm `acompas` no tiene usuarios a fecha de esta decisión. `--import-realm` usa `IGNORE_EXISTING`: sobre un realm ya existente, el JSON no se aplica. Por eso la ventana barata es ahora, antes de ACO-015; después habría que recrear el volumen y los usuarios, o aplicar el cambio al realm vivo, que ACO-012 §5 deja fuera de su alcance.

Es un cambio de seguridad: requiere decisión conjunta y ADR (Plan de Trabajo §8 y §9).

Hechos verificados el 31-oct-2026 con Keycloak 26.8.0 en un contenedor desechable:

- La importación limpia deja `default-roles-acompas` con `offline_access`, `uma_authorization`, `view-profile` y `manage-account`.
- Declarar el rol por defecto sin `offline_access`, conservando el resto, funciona. Requiere declarar `uma_authorization` antes en `roles.realm`; si no, el importador falla con `Unable to find composite realm role: uma_authorization`.
- `--import-realm` usa `IGNORE_EXISTING`: sobre un realm con datos, el JSON no aplica.
- El realm `acompas` no tiene usuarios en este momento.

## Decisión

1. **Momento (D1-A).** El cambio se aplica antes de ACO-015, en el Sprint 1. Es la ventana en la que el realm no tiene usuarios y basta una reimportación limpia. Si, por una incidencia operativa o porque A no cupo antes del congelado, el cambio se aplicara sobre un realm ya existente, la única vía que este ADR autoriza es recrear el volumen de Keycloak y, si los hay, volver a crear los usuarios de desarrollo con sus roles y TOTP. No autoriza aplicar el cambio mediante la Admin API: ACO-012 §5 la deja fuera y usarla exigiría una decisión posterior; la consulta de verificación de `check-realm.sh` no es una aplicación del cambio. El escenario del Sprint 2 (D1-C) se descarta: no aporta ninguna ventaja y encarece la corrección.

2. **Alcance (D2-A).** Se retira `offline_access` solo de los composites de `default-roles-acompas`. Se conservan `uma_authorization`, `view-profile` y `manage-account`. No se toca `defaultOptionalClientScopes` ni los scopes de los clientes integrados: sin el rol, el scope queda inerte, y esos cambios añaden superficie y dependen de valores por defecto que Keycloak puede variar en una actualización. El rol `offline_access` sigue existiendo en el realm y podrá asignarse de forma expresa a un usuario o cuenta de servicio si alguna integración lo necesita.

3. **Vehículo (D3-A).** Es una corrección de ACO-012, no un ACO nuevo. Se amplía `docs/aco/ACO-012.md` con P16, como primer commit de la PR de implementación. La PR de este ADR cierra #99; la de implementación cierra #93. No se toca la matriz del Documento Operativo ni se añade un número de ACO. La dependencia `015 ← 012/013` ya cubre el orden.

4. **Implementación del JSON.** En `roles.realm` se declara `uma_authorization` antes de `default-roles-acompas`. El rol por defecto se declara como compuesto por `uma_authorization` y los roles de cliente `view-profile` y `manage-account` del cliente `account`, sin `offline_access`. El rol `offline_access` no se declara ni se elimina: Keycloak lo mantiene como rol de realm y debe seguir existiendo. La importación limpia debe resolver los composites de `account`; si no lo hace, la PR no se acepta hasta corregir el orden o la forma de declararlos.

5. **Verificación (D4-A).** `scripts/check-realm.sh` consultará por la Admin API los composites de `default-roles-acompas` en el realm en marcha y comprobará:

   - que `offline_access` no aparece;
   - que `uma_authorization`, `view-profile` y `manage-account` siguen presentes;
   - que el rol `offline_access` sigue existiendo en el realm.

   No se comparará el conjunto exacto de composites: Keycloak puede añadir roles en una actualización y una igualdad estricta produciría un falso negativo, por el mismo motivo que descarta D2-C. La revisión comprobará también el JSON importado. El procedimiento de reimportación ya está documentado en `infra/keycloak/README.md`; se mantiene el comando exacto y se corrige el párrafo que hoy afirma que `offline_access` sigue en el rol por defecto.

   La comprobación funcional —una petición con `scope=openid offline_access` contra un cliente que tenga el scope no debe devolver un refresh token offline— requiere un usuario. Este ACO no crea usuarios (ACO-012 P2; ADR-009). Se documenta en la PR de #93 y se ejecuta en ACO-015, cuando existan usuarios con TOTP; #93 recogerá el diferimiento en su criterio de aceptación para que su cierre no aparente incumplir la lista.

6. **Relación con #102/ADR-017.** La restricción del email se decide e implementa de forma independiente conforme a ADR-017. Este ADR no la autoriza ni depende de ella para su validez. La permanencia de `manage-account` deja abierto un riesgo que ADR-017 debe abordar; se recoge en «Consecuencias».

7. **Documentación y alcance.** Se actualizan `infra/keycloak/import/acompas-realm.json`, `scripts/check-realm.sh`, `infra/keycloak/README.md` y `docs/aco/ACO-012.md` (P16). No se modifica la ficha de ACO-013: su P8 ya remite el rol del realm a ACO-012. No se añaden dependencias ni se modifica la CI. El registro del Plan de Trabajo §9 se actualiza después del merge, según la Estrategia de actualización documental.

## Alternativas consideradas

- **D1-B (después del congelado del 6):** aceptable solo si A no cabe. El coste es recrear el volumen y, si hay usuarios, volver a darlos de alta; no una migración. No se prefiere porque la ventana sin usuarios es más barata.
- **D1-C (Sprint 2):** descartada. Aplaza una decisión ya identificada, obliga a crear usuarios con el rol heredado y encarece la corrección sin ninguna ventaja.
- **Aplicar el cambio al realm vivo por Admin API:** descartada para este ACO. ACO-012 §5 excluye su uso y exigiría una decisión posterior; además, el realm no tiene usuarios y la reimportación limpia es más simple.
- **D2-B (quitar el scope de `defaultOptionalClientScopes`):** descartada. Es defensa en profundidad, pero sin el rol no cambia el resultado y añade superficie.
- **D2-C (quitarlo también de los clientes integrados):** descartada por el mismo motivo, y porque depende de valores por defecto que Keycloak puede cambiar en una actualización.
- **D3-B (ACO nuevo):** descartada. `default-roles-acompas` es configuración del realm que produjo ACO-012; un ACO nuevo obliga a tocar la matriz y el Documento Operativo sin aportar nada.
- **D4-B (solo comprobación manual):** descartada. No detecta regresiones ni un rol por defecto vacío o mal declarado.
- **D4-C (test con usuario sintético y TOTP):** descartada para este ACO. Obliga a automatizar TOTP y a crear usuarios, lo que choca con ACO-015 y con la regla de no crear usuarios fuera de él.
- **Comprobar el conjunto exacto de composites:** descartada. Una actualización de Keycloak puede añadir un composite y romper la comprobación sin que haya un problema real.
- **Eliminar el rol `offline_access`:** descartada. Debe seguir existiendo para asignaciones expresas; eliminarlo es un cambio mayor y puede romper integraciones.
- **Quitar `manage-account` del rol por defecto:** descartada. Rompe la consola de cuenta y es una medida más amplia que la necesaria; la restricción del email se decide en ADR-017.
- **Desactivar `admin-cli` o la concesión directa:** fuera de esta decisión. La retirada del rol cierra la vía del token offline; el resto de controles son de otros ACO y ADR.

## Consecuencias

- Ningún usuario hereda `offline_access`: no se emiten tokens offline por defecto, ni contra `acompas-frontend` ni contra los clientes integrados.
- El rol `offline_access` sigue existiendo. Una integración que lo necesite deberá asignarlo a un usuario o cuenta de servicio concreta, con revisión expresa.
- Los clientes integrados conservan el scope, pero queda inerte sin el rol. Si en el futuro se asigna el rol a un usuario, esos clientes podrán emitir tokens offline; es el comportamiento deseado de una asignación expresa.
- Quien tenga el realm importado en local deberá recrear el volumen `acompas_keycloak_data` para aplicar el JSON. Después de ACO-015, además, habrá que volver a crear los usuarios y reconfigurar TOTP.
- ACO-015 no debe volver a añadir `offline_access` al rol por defecto ni asignarlo de forma inadvertida al crear usuarios. Al ampliarse, su ficha deberá recoger esa restricción.
- La permanencia de `manage-account` deja abierto un riesgo que ADR-017 debe abordar: si el email es editable por el usuario, la lista blanca puede eludirse cambiándolo. ADR-016 no depende de esa decisión para su validez.
- La comprobación funcional del token offline queda pendiente hasta que existan usuarios; se documenta y se ejecuta con ACO-015.
- No se añaden dependencias ni se modifica la CI. El registro del Plan de Trabajo §9 se actualiza después del merge.

## Fuera de esta decisión

- Quitar `offline_access` de `defaultOptionalClientScopes` o de los clientes integrados.
- Eliminar el rol `offline_access`.
- Desactivar `admin-cli` o la concesión directa de contraseña.
- Aplicar el cambio al realm vivo por Admin API.
- La lista blanca, el perfil de email y el mecanismo de acceso de ACO-015 (#102/ADR-017).
- La creación de usuarios, la asignación de roles y TOTP (ACO-015).
- El despliegue en producción, TLS y el modo `start`.
- Cambios en el cliente `acompas-frontend` (ACO-013).
- La CI: no se añade un job que levante Keycloak.

## Documentos afectados

- `infra/keycloak/import/acompas-realm.json`
- `scripts/check-realm.sh`
- `infra/keycloak/README.md`
- `docs/aco/ACO-012.md` (P16)
- Plan de Trabajo §9 (registro de ADR)
