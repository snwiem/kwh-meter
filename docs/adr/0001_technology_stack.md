# ADR 0001 — Technology Stack

## Status

Accepted

## Date

2026-09-20

## Context

The kwh-meter application is a small, single-household energy meter tracking tool intended to run exclusively on an internal home network. It will never be exposed to the internet. The deployment must be containerized for ease of setup and maintenance. The primary developer is more familiar with Python than Node.js, and has a clear preference for Vue as the frontend framework. A dedicated external database is preferred over an embedded solution to keep concerns separated and data persistent across container restarts.

## Decision

The following technology stack was chosen:

### Deployment
- **Docker Compose** — the application is packaged as a set of containers orchestrated via `docker-compose.yml`.
- No reverse proxy or TLS termination is required given the internal-only deployment.
- The compose setup will consist of at minimum three services: `frontend`, `backend`, `db`.

### Backend
- **Python** with **FastAPI** as the web framework.
- FastAPI was chosen over Flask for the following reasons:
  - Modern, async-first design fits well with an API-first architecture.
  - Automatic OpenAPI/Swagger UI generation (`/docs`) provides a built-in way to explore and test the API during development without requiring the frontend to be ready.
  - Built-in request/response validation via **Pydantic** models reduces boilerplate.
  - First-class PostgreSQL support via `SQLAlchemy` (async) and `asyncpg`.

### Frontend
- **Vue 3** with **TypeScript**.
- Vue was chosen as the definite preference of the developer.
- The frontend is served as a separate container (e.g. via `nginx` serving a built Vue app or a dev server during development).
- Communication with the backend is done via the FastAPI REST API.

### Database
- **PostgreSQL** as a dedicated container.
- Chosen over embedded SQLite to keep data storage separated from the application layer, making backups, inspection, and future migrations easier.
- The backend connects to PostgreSQL using SQLAlchemy with an async driver (`asyncpg`).

## Consequences

- The developer will need to learn FastAPI, but the automatic docs and Pydantic validation make the learning curve manageable for a project of this scope.
- Three containers need to be maintained (frontend, backend, db), but Docker Compose makes this straightforward.
- The internal-only deployment means no need to handle TLS, authentication, or rate limiting at this stage.
- If the app ever needs to be exposed externally, an ADR must be written to address authentication, authorization, and TLS termination before doing so.
