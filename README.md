# My Events

Platform for managing events, sessions, speakers, and registrations.

## Repository layout

Monorepo organized by domain:

- [`backend/`](backend/) — REST API with FastAPI on Python 3.12.

## Requirements

- Docker + Docker Compose v2
- Make

## Quick start

```bash
cp backend/.env.example backend/.env
make dev
```

The API is exposed at <http://localhost:8000>, with docs at <http://localhost:8000/api/docs>.

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
make migrate m="message"        # alembic autogenerate + upgrade head
make upgrade                    # alembic upgrade head
make downgrade                  # alembic downgrade -1
```

Targets run against the `docker-compose.yml` + `docker-compose.dev.yml` stack.

## Per-service documentation

- [Backend](backend/README.md) — stack, configuration, and endpoints.
