# kwh-meter

A small, self-hosted, **mobile-first** web application to manually track the reading (*Zählerstand*) of a single electricity meter. Readings are recorded over time and can be browsed, edited, deleted, and exported — primarily operated from a phone.

There is no authentication, authorization, or multi-tenancy: the app manages exactly **one active meter**, configured via a JSON file.

## Features

- **One active meter** — identity and address supplied via a JSON config file.
- **Record a reading** — timestamp, value (kWh), and an optional comment; the value is validated against neighbouring readings (a meter only ever counts upward).
- **List readings** — newest first, with infinite scroll.
- **Detail view** — read-only page for a single reading, with edit/delete actions in the top bar.
- **Edit a reading** — pre-filled form (`PUT`); validation matches the create flow.
- **Delete a reading** — with a confirmation dialog.
- **Export** — download all readings as TSV or JSON.
- **Analyse** — energy-consumption overview page (`📊 Analyse` in the burger menu): each interval between consecutive readings rendered as a bar (width ∝ duration, height = energy in kWh, average power in kW shown per interval), with a date/time range selector (snap-to-reading, auto-clamped FROM < TO) above the chart. See [docs/feature/0010](docs/feature/0010_energy_consumption_overview.md) and [docs/feature/0011](docs/feature/0011_date_range_selector.md).
- **Benachrichtigungen** — notification plan page (`🔔 Benachrichtigungen` in the burger menu): a list of daily times at which the backend reminds you via a self-hosted [ntfy](https://ntfy.sh) push notification to record a new reading; the plan is edited in the UI and persisted in the database. See [docs/feature/0012](docs/feature/0012_notification_plan.md).
- German UI, mobile-first (Vue 3 + Vite).

## Repository layout

```
.
├── backend/                  FastAPI backend (Python 3.12)
│   ├── app/                  application code
│   │   ├── main.py           app entrypoint + startup/seed logic
│   │   ├── config.py         meter-config loading
│   │   ├── models.py         SQLAlchemy models (Meter, Reading)
│   │   ├── schemas.py        Pydantic schemas
│   │   └── routers/          API endpoints (meter, readings, export)
│   ├── alembic/              database migrations
│   ├── tests/                pytest suite (in-memory SQLite via aiosqlite)
│   ├── Dockerfile
│   └── pyproject.toml        dependencies (managed with uv)
├── frontend/                 Vue 3 + TypeScript + Vite SPA
│   ├── src/                  app source
│   │   ├── App.vue           global top bar + menu
│   │   ├── router/           routes
│   │   └── views/            page components
│   ├── public/               static assets (favicon)
│   ├── Dockerfile            multi-stage build → nginx
│   ├── nginx.conf            SPA fallback + /api proxy
│   ├── package.json
│   └── vite.config.ts
├── docs/                     feature specs, ADRs, domain concept
│   ├── feature/              one file per feature/requirement
│   ├── adr/                  architecture decision records
│   └── domain-concept.md     authoritative domain terminology
├── .github/                  issue templates
├── docker-compose.yml        full stack (db + backend + frontend + ntfy)
├── meter-config.example.json template for the meter config
├── .env.example              environment variables
└── AGENTS.md                 agent/project conventions
```

## Domain model

The two core objects are **Meter** (*Stromzähler*) and **Reading** (*Ablesung*). See [`docs/domain-concept.md`](docs/domain-concept.md) for the authoritative description and business rules.

## Build & deploy

### With Docker Compose (recommended)

1. Create the meter config from the template:

   ```bash
   cp meter-config.example.json meter-config.json
   # edit meter-config.json — fill in your Zählernummer and address
   ```

2. Build and start the stack:

   ```bash
   docker compose up -d --build
   ```

   | Service  | Description                                   | Host port |
   |----------|-----------------------------------------------|-----------|
   | `db`      | PostgreSQL 16                                 | (internal) |
   | `backend` | FastAPI; runs Alembic migrations on start     | `8000`    |
   | `frontend`| nginx serving the built SPA, proxying `/api`  | `5173`    |
   | `ntfy`    | self-hosted push-notification server          | `8080`    |

3. Open the app at <http://localhost:5173>. The backend API is at <http://localhost:8000> (health check: `/health`).

4. Set up reading reminders (optional but recommended): create a `.env` file next to `docker-compose.yml` so compose can substitute the notification settings, and point `NTFY_PUBLIC_URL` at the **LAN address of the host** — the `http://localhost:8080` default cannot be reached from your phone:

   ```bash
   # .env
   NTFY_PUBLIC_URL=http://192.168.1.10:8080   # LAN address of the ntfy server
   NTFY_TOPIC=kwh-meter-readings              # topic to subscribe to in the ntfy app
   TZ=Europe/Berlin                           # timezone reminder times fire in (default)
   ```

   Then open `🔔 Benachrichtigungen` in the app and subscribe in the ntfy phone app using the server URL and topic shown there (the deep link opens the app directly). Reminder times fire in the `TZ` timezone.

The meter config is mounted read-only into the backend at `/config/meter.json` (see `KWH_METER_CONFIG`). Database migrations (`alembic upgrade head`) run automatically before the backend serves requests.

### Running inside a Distrobox

If you operate the container stack from inside a [Distrobox](https://github.com/89luca89/distrobox) container, the nested container runtime can fail to create namespaces (e.g. `newuidmap: Operation not permitted` with rootless Podman/Docker). In that case, run the container commands on the **host** via `distrobox-host-exec`:

```bash
# Build and start the stack on the host
distrobox-host-exec docker compose up -d --build

# Inspect running services
distrobox-host-exec docker compose ps

# Stop the stack
distrobox-host-exec docker compose down
```

Use `podman-compose` instead of `docker compose` if that is what your host uses. All other commands (the local `uv`/`npm` development workflow and tests) run normally inside the distrobox.

### Local development (without Docker)

**Backend** (requires Python ≥ 3.12 and [`uv`](https://docs.astral.sh/uv/)):

```bash
cd backend
uv sync                      # install dependencies
export DATABASE_URL=postgresql+asyncpg://kwh:kwh@localhost:5432/kwh
export KWH_METER_CONFIG=/path/to/meter-config.json
uv run uvicorn app.main:app --reload
```

Run the test suite (uses an in-memory SQLite database, no Postgres needed):

```bash
cd backend
uv run pytest
```

**Frontend** (requires Node 22):

```bash
cd frontend
npm install
npm run dev                  # dev server on :5173, proxies /api → localhost:8000
```

Production build (type-check + bundle):

```bash
cd frontend
npm run build                # vue-tsc && vite build → dist/
```

## Documentation

- **Feature requirements** — [`docs/feature/`](docs/feature/)
- **Architecture decisions** — [`docs/adr/`](docs/adr/)
- **Domain terminology** — [`docs/domain-concept.md`](docs/domain-concept.md)