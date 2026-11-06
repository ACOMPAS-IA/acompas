# ADR-018 — Corrección del rol por defecto tras la importación del realm

Estado: propuesto

Sustituido por: —

Origen: Decisión conjunta #126 (7–9 nov 2026; pendiente de objeción al abrir esta PR). Corrige el mecanismo de ADR-016 P16 y abre una excepción acotada a su D1-A; mantiene D2-A (los clientes conservan el scope) y D4-A (comprobación funcional). Implementación en ACO-012.

Relacionados: ADR-016 (retirada de `offline_access`), ADR-017 (aplicación del perfil de usuario tras la importación), ADR-001 (Keycloak como custodio de la correspondencia email↔UUID); ACO-012 y ACO-015.

## Contexto

ADR-016 decidió retirar `offline_access` del rol por defecto del realm y fijó como mecanismo declarar el rol por defecto sin ese composite en `infra/keycloak/import/acompas-realm.json` (P16). La implementación se mergeó en #115 y `scripts/check-realm.sh` pasó a comprobar los composites de `default-roles-acompas`.

Al ejecutar la comprobación funcional que ADR-016 difirió a ACO-015 (AC-14), el resultado es que **los usuarios siguen heredando `offline_access`**:

- Una importación limpia deja como `defaultRole` real del realm `default-roles-acompas-1`, no el rol declarado `default-roles-acompas`.
- `default-roles-acompas-1` es compuesto por `offline_access`, `view-profile` y `manage-account`.
- Un usuario recién creado hereda `offline_access`; una petición con `scope=openid offline_access` contra el cliente integrado `account` devuelve un refresh token offline (`refresh_expires_in=2592000`, `typ=Offline`).
- `scripts/check-realm.sh` no lo detecta porque consulta los composites de `default-roles-acompas`, no el `defaultRole` que Keycloak asigna de verdad.

Hechos verificados el 7-nov-2026 con Keycloak 26.8.0, la versión fijada en Compose, en contenedores desechables con importación limpia:

1. **JSON actual (sin `defaultRole`).** Keycloak crea `default-roles-acompas-1` y lo asigna como rol por defecto. Los usuarios heredan `offline_access`.
2. **Añadir `"defaultRole": {"name": "default-roles-acompas"}`.** El rol por defecto efectivo pasa a ser el declarado, pero sus composites quedan con `offline_access`, `uma_authorization`, `view-profile` y `manage-account`.
3. **Declarar `offline_access` como rol y como client scope** para que se omita `setupOfflineTokens`. El rol por defecto queda sin `offline_access` y el rol sigue existiendo, pero el scope `offline_access` desaparece de los `optionalClientScopes` de los clientes integrados (`admin-cli`, `account`, etc.). Una petición con el scope devuelve `invalid_scope`, no el escenario de «cliente con el scope pero sin token offline» que exige ADR-016 D4-A.
4. **Añadir `defaultOptionalClientScopes`** para recuperar el scope. No funciona: el import aplica ese campo después de crear los clientes y estos siguen sin `offline_access`.
5. **`defaultRole` explícito y retirada del composite por la Admin API.** El rol por defecto efectivo pasa a ser `default-roles-acompas` y sus composites quedan `uma_authorization`, `view-profile` y `manage-account`; el rol `offline_access` sigue existiendo. Un usuario nuevo con TOTP pendiente y luego sin él obtiene un login normal con `refresh_expires_in=1800` y `typ=Refresh`, y `scope=openid offline_access` contra `admin-cli` devuelve `not_allowed` («Offline tokens not allowed for the user or client»), no un refresh token offline. La retirada es idempotente.

Causa en el importador de Keycloak 26.8.0:

- `RealmManager.importRealm` crea el rol por defecto y después llama a `setupOfflineTokens` **antes** de importar `roles.realm`.
- `KeycloakModelUtils.setupOfflineRole` crea `offline_access` si no existe y lo añade al rol por defecto con `realm.addToDefaultRoles`.
- `RepresentationToModel.importRoles` solo **añade** composites; nunca los elimina.
- `RepresentationToModel.createRole` ignora los composites del `defaultRole`.

Por tanto, la comprobación de ADR-016 se hizo sobre el rol declarado y no sobre el rol que Keycloak asigna por defecto: es el mismo falso positivo que `check-realm.sh`. El mecanismo que autoriza ADR-016 no puede cumplir a la vez el rol por defecto sin `offline_access` y la conservación del scope en los clientes integrados (D2-A).

Es un cambio de seguridad: decisión conjunta y ADR (Plan de Trabajo §8 y §9). ADR-016 está aprobado y no se edita: este ADR lo corrige en el punto necesario y mantiene el resto.

## Decisión

1. **Vehículo (D1-A).** Es una corrección de ACO-012, no un ACO nuevo (ADR-016 D3-A). Se amplía `docs/aco/ACO-012.md` (P16 corregido o P18) como primer commit de la PR de implementación. No se toca la matriz del Documento Operativo ni se añade un número de ACO.

2. **Mecanismo (D2-A).** El JSON declara `"defaultRole": {"name": "default-roles-acompas"}` para que el rol por defecto efectivo sea el declarado y no `default-roles-acompas-1`. El importador seguirá añadiendo `offline_access` al rol por defecto; el composite se retira después de la importación con `scripts/apply-default-role.sh` por la Admin API.

   Esta es la excepción a ADR-016 D1-A y a ACO-012 §5: se limita a los composites del rol por defecto del realm `acompas`, en local/demo, y no reabre el uso general de la Admin API. El resto de la configuración del realm sigue viniendo del JSON y de `scripts/apply-user-profile.sh`.

3. **Alcance del script (D3-A).** `scripts/apply-default-role.sh`:

   - lee el realm, obtiene el nombre del `defaultRole` efectivo y consulta sus composites;
   - si `offline_access` está presente, lo elimina con `DELETE /admin/realms/acompas/roles/{rol}/composites` usando la representación del rol;
   - es idempotente: si ya no está, termina con éxito sin mutar nada;
   - no elimina el rol `offline_access`, no toca ningún otro composite, no cambia `defaultOptionalClientScopes` ni los clientes integrados, y no modifica el resto del realm;
   - solo admite `localhost` o `127.0.0.1`, toma el puerto de `KEYCLOAK_PORT` y las credenciales de administrador de desarrollo de `.env`, y no imprime credenciales ni el contenido de `.env`;
   - no añade dependencias: bash, curl y python3;
   - falla con código distinto de cero y un mensaje claro si el realm no está importado, si la Admin API no responde o si la verificación posterior no se cumple.

4. **Verificación (D4-A).** `scripts/check-realm.sh` consulta el `defaultRole` **efectivo** (`GET /admin/realms/acompas` → `defaultRole.name`) y comprueba sus composites:

   - `offline_access` no aparece;
   - `uma_authorization`, `view-profile` y `manage-account` siguen presentes;
   - el rol `offline_access` sigue existiendo en el realm.

   No se compara el conjunto exacto de composites, por el mismo motivo que ADR-016 D4-A. La comprobación funcional de AC-14 se ejecuta con un usuario local con TOTP: una petición con `scope=openid offline_access` contra un cliente que ofrezca el scope **no debe devolver un refresh token offline**. Con el composite retirado, Keycloak rechaza la petición con `not_allowed` («Offline tokens not allowed for the user or client») o no emite token offline en el flujo de código; en ningún caso devuelve `typ=Offline`. Un login sin ese scope sigue emitiendo un refresh token normal (`refresh_expires_in=1800`, `typ=Refresh`).

5. **Orden y reimportación (D5-A).** Tras una importación limpia: `scripts/apply-user-profile.sh` (P17), `scripts/apply-default-role.sh` y `scripts/check-realm.sh`. `infra/keycloak/README.md` y la sección de Keycloak de `README.md` y `README.es.md` documentan ambos pasos como obligatorios y actualizan el procedimiento de reimportación.

   El script corrige también un realm vivo sin recrear usuarios. Para partir del JSON y dejar el entorno reproducible se puede recrear el volumen de Keycloak y volver a crear los usuarios locales no versionados (ADR-016 D1-A). Los usuarios siguen siendo sintéticos y no se versionan (ADR-008).

   La retirada del composite impide emitir **nuevos** refresh tokens offline, pero no revoca los ya emitidos: un token offline existente sigue siendo válido hasta su caducidad. En local/demo se parte de un realm sin usuarios con tokens offline o se recrea el volumen; la revocación de tokens ya emitidos en otros entornos queda fuera de esta decisión.

6. **Datos y seguridad.** No se usan datos reales ni secretos en el repositorio. Los usuarios de la comprobación son locales y sintéticos. El script no registra credenciales, emails ni contenido de `.env`.

## Alternativas consideradas

- **Solo importación, declarando `offline_access` como rol y client scope:** descartada. Deja el rol por defecto limpio sin Admin API, pero los clientes integrados pierden el scope, contra ADR-016 D2-A, y AC-14 pierde su escenario de comprobación.
- **Solo `defaultRole` en el JSON:** descartada. El rol por defecto efectivo sigue heredando `offline_access`.
- **Aceptar el rol heredado:** descartada. Incumple AC-14 y el objetivo de ADR-016; mantiene refresh tokens offline de 30 días.
- **Quitar `offline_access` de los clientes integrados o de `defaultOptionalClientScopes`:** descartada por ADR-016 D2-B y D2-C. Sin el rol, el scope queda inerte; tocarlo añade superficie y depende de valores por defecto que Keycloak puede variar.
- **Extensión o SPI de Keycloak:** descartada. Añade un componente y una dependencia del stack, y exige un ADR distinto.
- **Aplicarlo a mano en la consola:** descartada. Rompe la reproducibilidad y deja el paso a merced de que alguien lo recuerde; el check lo detectaría, pero no lo corregiría.
- **Eliminar el rol `offline_access`:** descartada. Debe seguir existiendo para asignaciones expresas (ADR-016).
- **Cambiar el nombre del rol por defecto para evitar el sufijo `-1`:** descartada. No evita que `setupOfflineRole` añada el composite y complica la lectura del realm.

## Consecuencias

- El realm deja de ser reconstruible solo desde el JSON importado: requiere `scripts/apply-user-profile.sh` y `scripts/apply-default-role.sh`. Es un uso acotado y deliberado de la Admin API, limitado a local/demo, y no reabre el resto de ACO-012 §5.
- `scripts/check-realm.sh` deja de dar el falso positivo: comprueba el rol que Keycloak asigna de verdad.
- Cualquier importación limpia posterior exige ejecutar los dos scripts y volver a crear los usuarios locales no versionados.
- AC-14 se puede cumplir y cerrar; #125 puede actualizarse y #20 cerrarse después.
- AC-14 de ACO-015 dice «no se ha modificado `default-roles-acompas`». Esa frase se refiere a que ACO-015 no corrige el realm por su cuenta: la retirada del composite es el entregable de ACO-012 (P16/P18) y la ejecuta su script autorizado, no ACO-015. La ficha de ACO-015 no cambia por este ADR.
- ADR-016 D2-A y D4-A siguen vigentes. Su D1-A queda corregido solo en este punto: el cambio del rol por defecto se aplica por Admin API, no solo por el JSON.
- No se añaden dependencias ni se modifica la CI. Las pruebas no usan red ni datos reales.

## Fuera de esta decisión

- Producción, TLS y el modo `start`.
- Quitar `offline_access` de `defaultOptionalClientScopes` o de los clientes integrados.
- Eliminar el rol `offline_access`.
- Desactivar `admin-cli` o la concesión directa de contraseña.
- Cambios en `acompas-frontend` (ACO-013), en el backend (ACO-014/ACO-015) o en el frontend (ACO-018).
- La creación de usuarios, la asignación de roles y TOTP (ACO-015).
- Cualquier otro cambio del realm por Admin API fuera de los dos scripts autorizados.

## Documentos afectados

- `docs/adr/ADR-018-correccion-rol-por-defecto-post-importacion.md` (este ADR)
- `docs/aco/ACO-012.md` (P16 corregido o P18; excepción a §5)
- `infra/keycloak/import/acompas-realm.json` (`defaultRole`)
- `scripts/apply-default-role.sh` (nuevo)
- `scripts/check-realm.sh` (rol por defecto efectivo)
- `infra/keycloak/README.md`
- `README.md` y `README.es.md` (sección de Keycloak)
- Plan de Trabajo §9 (registro de ADR, después del merge)
