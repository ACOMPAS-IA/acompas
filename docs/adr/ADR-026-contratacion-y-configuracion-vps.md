# ADR-026 — Contratación y configuración del VPS

Estado: aprobado

Sustituido por: —

Origen: Issue #198 y Arquitectura del Sistema v0.10 §16 nº 17, que deja abiertos «el criterio de contratación y la configuración», y §16 nº 11, que da por adoptado el reparto de entornos sin redactarlo. Documento Operativo Sprint 2 v0.4 §6: fila del ADR, responsable Miguel, revisión de Luis, y fila de ACO-054, 8–10 h, que este ADR desbloquea. No abre ventana de 48 h: la matriz ya asigna el ADR y esto es su redacción. Tres de sus puntos no los fija ninguna fuente y siguen el procedimiento del Plan de Trabajo §8, anotados en #198.

Relacionados: ADR-005 (el original no se persiste), ADR-008 (sin datos reales hasta las salvaguardas), ADR-011 (autenticación y roles), ADR-015 (gestión de secretos), ADR-020 (entorno de ejecución del backend), ADR-025 (derecho al olvido y el límite de las copias); ACO-054, ACO-055, ACO-056; #92, #165.

## Contexto

La Arquitectura §13 fija el servidor (VPS Hetzner CPX41, 16 GB de RAM, región EU), el entorno de desarrollo (Docker Compose en local; nadie depende del VPS), la fecha de contratación (~2 semanas antes de la Demo ACANPAN de diciembre) y las copias (cifradas, en proveedor europeo). §16 nº 17 dice que falta el criterio de contratación y la configuración; §16 nº 11, que falta redactar el ADR del entorno.

El Plan de Proyecto §5 presupuesta 30–40 €/mes para el CPX41, 5 €/mes de copias y ~5 €/mes de dominio y servicios básicos, con 10–15 €/año de registro; §7 sitúa la contratación a finales de noviembre de 2026. La fila ACO-054 del Documento Operativo Sprint 2 depende de este ADR, y detrás están ACO-055 (staging) y ACO-056 (demo).

Dos cosas no están medidas. El precio del CPX41 cambia y no hay cuenta que lo consulte: la API de precios de Hetzner exige token y la cuenta se abre al contratar. Y no hay medida del consumo de memoria del conjunto: lo medido es la imagen del backend, 3,20 GB con los modelos dentro (ADR-020), y los componentes que §13 dice que conviven en el servidor.

ADR-008 y la regla R-01 del arnés siguen vigentes: ningún entorno usa documentos reales hasta que la anonimización, el derecho al olvido y el registro de auditoría estén operativos.

## Decisión

**1. Criterio de contratación.** Un servidor europeo que sostenga a la vez PostgreSQL con pgvector, sentence-transformers con los modelos, Presidio, Keycloak, el backend y el frontend. El mínimo no es una máquina de 1 GB: la imagen del backend pesa 3,20 GB con los modelos dentro y hay que sumar la base y el resto de servicios. La elección ya está hecha por la Arquitectura §13 —Hetzner Cloud, CPX41, 16 GB de RAM, región EU— y este ADR no la reabre: fija el criterio con el que se comprueba y deja en ACO-054 la medida real de memoria y disco.

**2. Precio y alta.** El presupuesto es 30–40 €/mes (Plan §5). El precio vigente se anota en ACO-054 el día de la contratación, con la factura, porque antes no hay cuenta. Si el precio o el modelo han cambiado y se sale del presupuesto, no se contrata por decisión propia: se anota en #198 y sigue el §8, porque compromete gasto. El alta se hace por consola o API; el plazo real se mide en ACO-054 y no mueve la fecha, que está fijada a finales de noviembre.

**3. Reparto de entornos.** Desarrollo: Docker Compose en local, sin depender del VPS (§13; R-33). Servidor: el entorno de **pruebas**, con **dos proyectos Compose** en la misma instancia, `ensayo` y `demo`, cada uno con su red, sus volúmenes y su fichero de entorno; comparten servidor y proxy, no datos. La producción no existe todavía y tendrá instancia propia cuando exista: entonces se cumplen las «instancias separadas» de §13 sin haberlas incumplido antes.

**4. Arranque en limpio de la demo.** Antes de la demo se baja el proyecto de ensayo con sus volúmenes y se levanta el de demo con la base vacía; los documentos son sintéticos (ADR-008). La demo nunca ve lo que quedó del ensayo. ACO-055 conserva el arranque reproducible —orden de `up`, migraciones y realm de Keycloak— para que el ensayo se pueda repetir; ACO-056 ensaya el recorrido sobre ese arranque.

**5. Red.** Solo se publican 443 y 80 (ACME y redirección). PostgreSQL, Keycloak, el backend y el servicio de modelos escuchan en la red interna de su proyecto, sin puerto publicado. Un proxy inverso termina TLS con Let's Encrypt y enruta por nombre: el dominio raíz a la demo y `ensayo.<dominio>` al ensayo. Cortafuegos del proveedor con 22, 80 y 443; SSH solo con clave, sin contraseña y sin acceso directo de root.

**6. Dominio.** `acompas-ia.es` es el canónico: el proyecto y sus pacientes son españoles y el `.es` es el registro de referencia, ya presupuestado. El `.org` no se contrata ahora; si se registra, redirige al `.es` y no aloja nada. Registrador y DNS se llevan desde una sola cuenta, con las cuentas nominales del punto 9; el registrador concreto se elige al contratar y se anota en ACO-054. No es #92: allí se decide la clave de Claude y su titularidad.

**7. Persistencia.** Persiste el volumen de PostgreSQL. El documento original no se persiste (ADR-005) y el temporal es efímero. El anonimizado de la demo va a un volumen efímero que se borra con el entorno: dónde se guarda y con qué tecnología sigue abierto en §16 nº 2, y ACO-054 no lo decide ni lo necesita para la demo.

**8. Copias.** Cifradas, en proveedor europeo (§13), diarias, fuera del servidor, con restauración probada en ACO-054. La retención y el proveedor concreto no los fija ninguna fuente: van al §8, anotados en #198. El derecho al olvido se verifica sobre los datos vivos y **no alcanza las copias**; es el límite que ADR-025 declara y este ADR no lo estrecha.

**9. Acceso.** Dos cuentas nominales, una por persona (Miguel, Luis), con clave SSH y sudo, sin cuentas compartidas ni contraseña. La consola del proveedor y el registrador están a nombre del responsable del proyecto, con la otra persona como contacto técnico. El fichero de la clave lo lee solo la cuenta que despliega.

**10. Clave.** `ANTHROPIC_API_KEY` vive en el servidor, fuera del repositorio y del contexto de construcción, en un fichero con permisos 600, y se inyecta solo al servicio `backend` (ADR-015 §1). No se copia a la imagen, no viaja en el fichero de Compose y no entra en Git. El mecanismo de producción —Docker secrets o gestor gestionado, con rotación— sigue pendiente en el ADR que anuncia ADR-015 §6, y este ADR no lo decide porque el VPS es el entorno de pruebas.

**11. Lo que no entra en el servidor.** Ningún documento real hasta que las salvaguardas de ADR-008 estén operativas. La demo usa documentos sintéticos y, si ACANPAN no confirma la demo, no se contrata.

## Lo que este ADR propone y no decide por sí solo

Tres puntos no los fija ninguna fuente y se registran en #198 con su línea de veredicto y su plazo, según el §8:

- **Ensayo y demo en la misma instancia**, en lugar de una segunda máquina.
- **Retención de las copias** y el proveedor concreto.
- **El proxy inverso**: Caddy, por ACME automático y configuración mínima, frente a nginx.

Si el §8 los cambia, se corrige este ADR antes del merge, no después.

## Alternativas consideradas

- **Segunda máquina para el ensayo.** Descartada: duplica el coste mensual y el presupuesto solo cubre un CPX41; la separación por proyecto Compose da entornos aislados sin segunda factura.
- **Un solo Compose para ensayo y demo.** Descartada: comparten base y configuración, y la demo dejaría de arrancar en limpio.
- **Producción en el mismo servidor.** Descartada: §13 pide instancias separadas y la demo no es producción.
- **Otro proveedor.** Descartada: §13 fija Hetzner en región EU y el presupuesto está calculado sobre él.
- **Esperar a §16 nº 2 para el almacenamiento del anonimizado.** Descartada: bloquearía ACO-054 por una decisión que la demo no necesita.

## Consecuencias

- ACO-054 contrata, despliega y anota precio, plazo y consumo real; ACO-055 deja el arranque reproducible; ACO-056 ensaya sobre él.
- Si el precio se sale de 30–40 €/mes o el CPX41 ya no existe, se para y va al §8: no se contrata por decisión propia.
- Las copias quedan sin retención fijada hasta que el §8 la resuelva; mientras tanto no se promete al paciente un borrado que las alcance.
- El derecho al olvido se sigue verificando sobre los datos vivos (ADR-025).
- La Arquitectura §13 y §16 nº 11 y 17 se corrigen en su próxima revisión, con su fila en el registro de seguimientos; el arnés se regenera después desde las fuentes.
- El registro de ADR del Plan de Trabajo §9 incorpora este ADR en la pasada de documentación, no en esta PR.

## Documentos afectados

Arquitectura del Sistema §13 y §16 nº 11 y 17; Plan de Trabajo §9, registro de ADR; Documento Operativo Sprint 2 §6, filas ACO-054 a ACO-056, sin ficha todavía; arnés `08-PLAN` y `03-REGLAS`, por regeneración. Casos de Uso no cambia.
