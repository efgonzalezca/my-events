# My Events

Platform for managing events, sessions, speakers, and registrations.

## Repository layout

Monorepo organized by domain:

- [`backend/`](backend/) — REST API with FastAPI on Python 3.12.
- [`frontend/`](frontend/) — SPA with React 19 + Vite + TypeScript + Tailwind CSS v4.

## Requirements

- Docker + Docker Compose v2
- Make

## Quick start

```bash
cp backend/.env.example backend/.env
make dev
```

This brings up the full dev stack (Postgres + backend + frontend):

- Frontend (Vite, hot reload): <http://localhost:5173>
- Backend: <http://localhost:8000>
- API docs: <http://localhost:8000/api/docs>

## Available targets

```bash
make help                       # list all targets
make dev                        # build + up the dev stack
make down                       # stop the stack
make logs                       # tail logs
make status                     # ps of the stack
make build                      # rebuild the backend
make lock                       # regenerate poetry.lock
make test                       # run pytest -v inside the backend
make test-frontend              # run vitest inside the frontend container
make migrate m="message"        # alembic autogenerate + upgrade head
make upgrade                    # alembic upgrade head
make downgrade                  # alembic downgrade -1
make seed                       # populate the database with demo data
make clean-db                   # truncate every domain table
```

After a fresh `make dev`, run `make seed` once to load demo users, events, sessions, speakers, and registrations. See [backend/README.md](backend/README.md#demo-data) for the credentials and what gets created.

Targets run against the `docker-compose.yml` + `docker-compose.dev.yml` stack.

## Per-service documentation

- [Backend](backend/README.md) — stack, configuration, and endpoints.
- [Frontend](frontend/README.md) — stack, scripts, routes, and decisions.
