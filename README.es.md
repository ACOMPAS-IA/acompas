# ACOMPAS

**Asistente conversacional de IA para pacientes con cáncer de páncreas.**

ACOMPAS ayuda a los pacientes con cáncer de páncreas a comprender su
documentación clínica y a prepararse mejor para sus consultas con el
oncólogo. No diagnostica ni sustituye el criterio médico: es una
herramienta de apoyo para la comprensión y la preparación.

🚧 **Proyecto en desarrollo.** Lanzamiento previsto: verano de 2027.
Más información: [acompas-ia.es](https://www.acompas-ia.es)

*[Read in English](README.md)*

---

## Qué es ACOMPAS

Un diagnóstico de cáncer de páncreas genera una gran cantidad de
documentación clínica llena de terminología especializada que puede
resultar difícil de comprender sin formación médica. ACOMPAS traduce
esa documentación a un lenguaje sencillo y ayuda a los pacientes a
preparar preguntas para sus consultas de oncología.

El proyecto está desarrollado por voluntarios, con carácter no
lucrativo, en colaboración con [ACANPAN](https://asociacioncancerdepancreas.org/),
la asociación española de pacientes con cáncer de páncreas.

## Cómo funciona (visión general)

- **Conversación asistida por IA**, con respuestas fundamentadas en
  guías clínicas y publicaciones médicas seleccionadas.
- **Privacidad desde el diseño**: los documentos clínicos se
  anonimizan antes de ser utilizados por el sistema. La identidad del
  paciente nunca se almacena en la base de datos de la aplicación.

Puedes encontrar más información sobre el proyecto en
[acompas-ia.es](https://www.acompas-ia.es).

## Estado del proyecto

Actualmente se encuentra en las primeras fases de desarrollo
(Fase 0 / Fase 1). Este repositorio se irá completando
progresivamente a medida que avance la implementación.

## Entorno de desarrollo

ACOMPAS utiliza Docker como entorno de desarrollo de referencia. El
objetivo es que todos los colaboradores puedan ejecutar los mismos
servicios localmente, independientemente del sistema operativo del
equipo anfitrión.

### Requisitos

- Git
- Docker Desktop con integración con WSL2 en Windows
- Docker Engine / Docker Compose en Linux o macOS

Para el flujo de desarrollo estándar no es necesario instalar
directamente Python, PostgreSQL ni Node.js en el equipo anfitrión.

### Primera configuración

Clona el repositorio y entra en el directorio del proyecto:

```bash
git clone git@github.com:ACOMPAS-IA/acompas.git
cd acompas
```

Crea el archivo de entorno local y mantenlo privado:

```bash
cp .env.example .env
chmod 600 .env
```

Inicia el entorno de desarrollo:

```bash
docker compose up -d --build
```

Comprueba los servicios en ejecución:

```bash
docker compose ps
```

El endpoint de salud del backend debe devolver:

```json
{"status":"ok"}
```

Puedes comprobarlo con:

```bash
curl http://localhost:8000/health
```

### Frontend

El frontend React se sirve en <http://localhost:5173> (o el puerto de
`FRONTEND_PORT`) y se recarga automáticamente al cambiar los ficheros
de `frontend/`.

Antes del primer `docker compose up`, crea la carpeta donde el
contenedor monta `node_modules`, para que sea de tu usuario:

```bash
mkdir frontend/node_modules
```

Si Docker ya la creó como `root`, bórrala y vuelve a crearla:

```bash
sudo rm -rf frontend/node_modules
mkdir frontend/node_modules
```

Sus comprobaciones se ejecutan dentro del contenedor:

```bash
docker compose exec frontend npm run lint
docker compose exec frontend npm run typecheck
docker compose exec frontend npm test
```

`node_modules` está en un volumen del contenedor. Después de cambiar
las dependencias del frontend, reconstruye el servicio y renueva ese
volumen:

```bash
docker compose up -d --build -V frontend
```

### Keycloak

`docker compose up -d` también arranca Keycloak en modo de desarrollo.
Su puerto solo se publica en `127.0.0.1`.

- Consola de administración: <http://localhost:8080> (o el puerto de
  `KEYCLOAK_PORT`).
- Credenciales del administrador inicial: `KEYCLOAK_BOOTSTRAP_ADMIN_USER`
  y `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD` de `.env`. Son solo de desarrollo
  y se aplican al crear el volumen de Keycloak; si las cambias después,
  borra el volumen.
- El realm de ACOMPAS es `acompas` (nombre visible `ACOMPAS`). Su
  documento de descubrimiento OIDC está en
  <http://localhost:8080/realms/acompas/.well-known/openid-configuration>
  (o el puerto de `KEYCLOAK_PORT`). Sus roles, 2FA, política de
  contraseñas, protección contra fuerza bruta y procedimiento de
  reimportación están documentados en `infra/keycloak/README.md`.

Cuando `docker compose ps` muestre `keycloak` como `healthy`, aplica la
configuración post-importación si acabas de reimportar el realm y comprueba
que responde con:

```bash
scripts/apply-realm-config.sh   # obligatorio tras una importación limpia
scripts/check-keycloak.sh
scripts/check-realm.sh
```

El primer script es idempotente: aplica el perfil de usuario (edición del email
restringida al administrador) y retira `offline_access` del rol por defecto
efectivo. Una reimportación limpia borra ambos cambios y hay que repetir el
paso. El segundo comprueba el realm `master`; el tercero, el realm `acompas`,
incluido su rol por defecto efectivo. Si cambias `KEYCLOAK_PORT` en `.env`, los
scripts lo toman de ahí.

Los datos de Keycloak se guardan en el volumen `acompas_keycloak_data` y se
conservan entre arranques. Para empezar de cero:

```bash
docker compose rm -sf keycloak
docker volume rm acompas_keycloak_data
```

El prefijo del volumen es el nombre del directorio del proyecto
(`acompas` por defecto). Tras recrear el volumen, ejecuta
`scripts/apply-realm-config.sh` antes de `scripts/check-realm.sh`; el perfil de
usuario y la retirada de `offline_access` del rol por defecto efectivo no
forman parte del JSON importado y una reimportación limpia borra ambos cambios.

Los realms en JSON que se coloquen en `infra/keycloak/import/` se
importan al arrancar. El realm de ACOMPAS está definido en
`infra/keycloak/import/acompas-realm.json`.

Keycloak se reinicia solo cada vez que arranca Docker
(`restart: unless-stopped`) y ocupa su puerto aunque no estés trabajando
en ACOMPAS. Para pararlo sin borrar sus datos:

```bash
docker compose stop keycloak
```

`docker compose up -d --build backend` no lo arranca;
`docker compose up -d` sí.

### Claude API (LLM gateway)

El backend solo llama a Claude API a través de `backend/app/services/llm_gateway/`.
La aplicación arranca sin estas variables; solo fallan las llamadas al gateway.

Para activarlas, rellena en tu `.env` local (la clave nunca se sube al repositorio):

- `ANTHROPIC_API_KEY`: tu clave de Anthropic.
- `LLM_MODEL`: el modelo de Claude. El proyecto aún no lo ha fijado (ADR pendiente).
- Opcionales: `LLM_MAX_OUTPUT_TOKENS` (1024), `LLM_TIMEOUT_SECONDS` (60) y
  `LLM_MAX_RETRIES` (2).

Solo se permite `ANTHROPIC_API_KEY` entre las variables `ANTHROPIC_*`. El
gateway rechaza cualquier otra con `not_configured` y registra solo su nombre.

Después recrea el backend para que las reciba:

```bash
docker compose up -d backend
```

### Rotación de la API key

La clave se gestiona manualmente (ADR-015). El titular de la clave del proyecto
es responsable de la rotación. Para rotar la clave o atender un incidente:

1. Revoca la clave en la consola de Anthropic.
2. Crea una clave nueva con el titular, la cuenta y el límite de gasto definidos.
3. Actualiza `ANTHROPIC_API_KEY` en tu `.env` local y mantén el archivo privado
   (`chmod 600 .env`). No lo subas nunca al repositorio.
4. Recrea el backend: `docker compose up -d backend`.
5. Comprueba `/health` y haz una llamada al gateway.
6. Revisa `docker compose logs backend` y ejecuta `scripts/check-secrets.sh`
   para revisar logs y commits.

Las claves personales son solo para desarrollo y la demo usa la clave del
proyecto (ADR-015 §2). La rotación automática queda fuera del Sprint 1.

### Umbrales de anonimización

El servicio de anonimización lee dos umbrales del entorno en cada llamada:

- `ANONYMIZATION_FINDING_THRESHOLD` (0,35): una detección por debajo se
  descarta como ruido y no se anonimiza.
- `ANONYMIZATION_DOCUMENT_THRESHOLD` (0,85): si la confianza del documento
  queda por debajo, el documento se retiene y no se devuelve texto anonimizado.

Ambos deben ser números entre 0 y 1, y el umbral de hallazgo no puede superar
al de documento; un valor inválido impide procesar. Se calibran con el corpus
sintético de ACO-051, así que ningún test fija su valor. En Docker, actualiza
`.env` y recrea el backend para cambiarlos.

### Detener el entorno

Para detener los servicios:

```bash
docker compose down
```

El volumen local de PostgreSQL se conserva salvo que se elimine
explícitamente.

### Flujo de desarrollo

Los cambios deben desarrollarse en ramas de funcionalidad y enviarse
mediante Pull Requests. Los pushes directos a `main` no forman parte
del flujo de trabajo habitual.

Ejemplo:

```bash
git switch -c feature/ACO-XXX-descripcion-corta
```

Antes de abrir un Pull Request, comprueba que los tests correspondientes
pasan correctamente y que el entorno Docker se inicia sin errores.

## Equipo

- **Miguel Martínez** — Fundador y responsable del proyecto.
- **Javier Pérez** — Consultor técnico y acompañamiento al equipo.
- **Luis del Olmo** — IA y procesamiento del lenguaje natural.

Buscamos ampliar nuestro equipo técnico de voluntarios, sobre todo en
backend y frontend. Si estás interesado en colaborar, ponte en contacto
con nosotros en info@acompas-ia.es.

## Colaboración

ACOMPAS se desarrolla en colaboración con **ACANPAN**, que aporta
contexto clínico, acceso a pacientes y validación del producto.

## Contacto

📧 [info@acompas-ia.es](mailto:info@acompas-ia.es)

## Licencia

Este proyecto está licenciado bajo [AGPL-3.0](LICENSE).
