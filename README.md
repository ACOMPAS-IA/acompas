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

- **Miguel Martínez** — Project lead and founder. Computer
  engineer, and also a pancreatic cancer patient himself — the
  experience that directly motivated ACOMPAS. Works alongside Javier
  on the project's technical direction and implementation.
- **Javier Pérez** — Technical lead (volunteer). Works alongside
  Miguel on the project's technical direction, and is responsible for
  the core implementation built so far, including the
  retrieval-augmented generation (RAG) pipeline (document ingestion,
  embeddings, and semantic search) and system architecture.

We are looking to grow our volunteer technical team (backend, AI/NLP,
frontend). If you're interested in contributing, reach out.

## Collaboration

ACOMPAS is developed in collaboration with **ACANPAN**, which
contributes clinical context, access to patients, and product
validation.

## Contact

📧 [info@acompas-ia.es](mailto:info@acompas-ia.es)

## License

This project is licensed under [AGPL-3.0](LICENSE).
