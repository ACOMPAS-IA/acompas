# ACOMPAS

**AI conversational assistant for pancreatic cancer patients.**

ACOMPAS helps pancreatic cancer patients understand their clinical
documentation and prepare better for consultations with their
oncologist. It does not diagnose or replace medical judgment: it is a
support tool for understanding and preparation.

🚧 **Project under development.** Expected launch: summer 2027.
More info: [acompas-ia.es](https://www.acompas-ia.es)

*[Leer en español](README.es.md)*

---

## What is ACOMPAS

A pancreatic cancer diagnosis brings a large amount of clinical
documentation full of specialized terminology that is difficult to
understand without medical training. ACOMPAS translates that
documentation into plain language and helps patients prepare questions
for their oncology consultations.

The project is built by volunteers, on a nonprofit basis, in
collaboration with [ACANPAN](https://asociacioncancerdepancreas.org/),
the Spanish pancreatic cancer patient association.

## How it works (high level)

- **AI-assisted conversation**, with responses grounded in curated
  clinical guidelines and medical publications.
- **Privacy by design**: clinical documents are anonymized before
  being used by the system. Patient identity is never stored in the
  application's database.

You can find more context about the project at
[acompas-ia.es](https://www.acompas-ia.es).

## Project status

Currently in early development (Phase 0 / Phase 1). This repository
will be populated progressively as implementation advances.

## Development setup

ACOMPAS uses Docker as the reference development environment. The goal
is that every contributor can run the same services locally regardless
of their host operating system.

### Requirements

- Git
- Docker Desktop with WSL2 integration on Windows
- Docker Engine / Docker Compose on Linux or macOS

Python, PostgreSQL and Node.js do not need to be installed directly on
the host for the standard development workflow.

### First setup

Clone the repository and enter the project directory:

```bash
git clone git@github.com:ACOMPAS-IA/acompas.git
cd acompas
```

Create the local environment file:

```bash
cp .env.example .env
```

Start the development environment:

```bash
docker compose up -d --build
```

Check the running services:

```bash
docker compose ps
```

The backend health endpoint should return:

```json
{"status":"ok"}
```

It can be checked with:

```bash
curl http://localhost:8000/health
```

### Frontend

The React frontend is served at <http://localhost:5173> (or the port in
`FRONTEND_PORT`) and reloads automatically when files in `frontend/`
change.

Before the first `docker compose up`, create the folder where the
container mounts `node_modules`, so that it belongs to your user:

```bash
mkdir frontend/node_modules
```

If Docker already created it as `root`, remove it and create it again:

```bash
sudo rm -rf frontend/node_modules
mkdir frontend/node_modules
```

Its checks run inside the container:

```bash
docker compose exec frontend npm run lint
docker compose exec frontend npm run typecheck
docker compose exec frontend npm test
```

`node_modules` lives in a container volume. After changing the
frontend dependencies, rebuild the service and renew that volume:

```bash
docker compose up -d --build -V frontend
```

### Keycloak

`docker compose up -d` also starts Keycloak in development mode. Its
port is only published on `127.0.0.1`.

- Administration console: <http://localhost:8080> (or the port set in
  `KEYCLOAK_PORT`).
- Initial administrator credentials: `KEYCLOAK_BOOTSTRAP_ADMIN_USER` and
  `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD` from `.env`. They are for
  development only and are applied when the Keycloak volume is created;
  if you change them later, remove the volume.
- The ACOMPAS realm is `acompas` (visible name `ACOMPAS`). Its OIDC
  discovery document is at
  <http://localhost:8080/realms/acompas/.well-known/openid-configuration>
  (or the port set in `KEYCLOAK_PORT`). Its roles, 2FA, password policy,
  brute-force protection and reimport procedure are documented in
  `infra/keycloak/README.md`.

Once `docker compose ps` shows `keycloak` as `healthy`, check that it
responds with:

```bash
scripts/check-keycloak.sh
scripts/check-realm.sh
```

The first script checks the `master` realm; the second checks the
`acompas` realm. If you change `KEYCLOAK_PORT` in `.env`, the scripts
read it from there.

Keycloak data is stored in the `acompas_keycloak_data` volume and is preserved
across restarts. To start from scratch:

```bash
docker compose rm -sf keycloak
docker volume rm acompas_keycloak_data
```

The volume prefix is the project directory name (`acompas` by
default).

JSON realms placed in `infra/keycloak/import/` are imported on startup.
The ACOMPAS realm is defined in
`infra/keycloak/import/acompas-realm.json`.

Keycloak restarts on its own every time Docker starts
(`restart: unless-stopped`) and holds its port even when you are not
working on ACOMPAS. To stop it without deleting its data:

```bash
docker compose stop keycloak
```

`docker compose up -d --build backend` does not start it;
`docker compose up -d` does.

### Claude API (LLM gateway)

The backend only calls Claude API through `backend/app/services/llm_gateway/`.
The application starts without these variables; only calls to the gateway fail.

To enable them, fill in your local `.env` (the key is never committed):

- `ANTHROPIC_API_KEY`: your Anthropic API key.
- `LLM_MODEL`: the Claude model. The project has not chosen it yet (pending ADR).
- Optional: `LLM_MAX_OUTPUT_TOKENS` (1024), `LLM_TIMEOUT_SECONDS` (60) and
  `LLM_MAX_RETRIES` (2).

Then recreate the backend so it receives them:

```bash
docker compose up -d backend
```

### Stopping the environment

To stop the services:

```bash
docker compose down
```

The local PostgreSQL data volume is preserved unless it is explicitly
removed.

### Development workflow

Changes should be developed on feature branches and submitted through
Pull Requests. Direct pushes to `main` are not part of the normal
workflow.

Example:

```bash
git switch -c feature/ACO-XXX-short-description
```

Before opening a Pull Request, make sure the relevant tests pass and
the Docker environment starts correctly.

## Team

- **Miguel Martínez** — Founder and project lead.
- **Javier Pérez** — Technical advisor and team support.
- **Luis del Olmo** — AI and natural language processing.

We are looking to grow our team of technical volunteers, especially in
backend and frontend. If you are interested in contributing, please
contact us at info@acompas-ia.es.

## Collaboration

ACOMPAS is developed in collaboration with **ACANPAN**, which
contributes clinical context, access to patients, and product
validation.

## Contact

📧 [info@acompas-ia.es](mailto:info@acompas-ia.es)

## License

This project is licensed under [AGPL-3.0](LICENSE).
