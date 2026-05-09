# My Events - Backend

REST API built with FastAPI on Python 3.12, packaged in Docker for development.

## Stack

- **Python** 3.12 (slim) + **Poetry** 2.4.0
- **FastAPI** 0.115.6 / **Uvicorn** 0.32.1 (standard, with `--reload` in dev)
- **Pydantic** 2.10.3 + **pydantic-settings** 2.7.0 for environment-based configuration
- **SQLModel** 0.0.22 / **SQLAlchemy** 2.0.36 / **psycopg** 3.2.3 (binary)
- **Alembic** 1.14.0 for database migrations
- **bcrypt** 4.2.1, **PyJWT** 2.10.1, **email-validator** 2.2.0
- **Pytest** 8.3.4 + **httpx** 0.28.1 (`dev` group)

## Layout

The backend follows a modular Clean Architecture: each business module owns
its `domain` / `application` / `infrastructure` / `interfaces` layers, and
cross-cutting concerns live under `shared/`.

```
backend/
├── alembic/
│   ├── env.py                           # imports module ORMs for autogenerate
│   └── versions/                        # migration revisions
├── app/
│   ├── core/
│   │   ├── config.py                    # Settings (BaseSettings) loaded from .env
│   │   └── logging.py                   # JSON formatter + request_id ContextVar
│   ├── interfaces/
│   │   └── http/
│   │       ├── auth.py                  # require_role(*roles) dependency factory
│   │       ├── error_handlers.py        # DomainError → HTTP mapping
│   │       ├── middleware.py            # RequestIdMiddleware (x-request-id + access log)
│   │       └── routes/
│   │           └── health.py            # GET /api/health
│   ├── modules/
│   │   ├── events/
│   │   │   ├── domain/                  # Event entity, status machine, value objects, errors
│   │   │   ├── application/             # use cases + DTOs
│   │   │   ├── infrastructure/          # SQLModel ORM, mappers, SqlEventRepository
│   │   │   └── interfaces/http/         # routes, schemas, FastAPI deps
│   │   └── identity/
│   │       ├── domain/                  # entities, value objects, repo Protocols, errors
│   │       ├── application/             # use cases + DTOs
│   │       ├── infrastructure/          # SQLModel ORM, mappers, SqlUserRepository
│   │       └── interfaces/http/         # routes, schemas, FastAPI deps
│   ├── shared/
│   │   ├── application/ports/auth.py    # PasswordHasher / TokenService Protocols
│   │   ├── domain/exceptions.py         # DomainError base
│   │   └── infrastructure/
│   │       ├── db.py                    # engine + session_scope
│   │       └── security/                # BcryptHasher, JwtTokenService
│   └── main.py                          # create_app() + /api APIRouter wiring
├── Dockerfile                           # multi-stage: base → development
├── entrypoint.sh
├── pyproject.toml
└── poetry.lock
```

## Configuration

Environment variables (see [.env.example](.env.example)):

| Variable                      | Default                                                       |
|-------------------------------|---------------------------------------------------------------|
| `APP_NAME`                    | `My Events API`                                               |
| `ENVIRONMENT`                 | `development`                                                 |
| `DEBUG`                       | `false`                                                       |
| `API_PREFIX`                  | `/api`                                                        |
| `HOST`                        | `0.0.0.0`                                                     |
| `PORT`                        | `8000`                                                        |
| `POSTGRES_USER`               | `miseventos`                                                  |
| `POSTGRES_PASSWORD`           | `miseventos`                                                  |
| `POSTGRES_DB`                 | `miseventos`                                                  |
| `DATABASE_URL`                | `postgresql+psycopg://miseventos:miseventos@db:5432/miseventos` |
| `JWT_SECRET_KEY`              | _(required, no default)_                                      |
| `JWT_ALGORITHM`               | `HS256`                                                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                                                          |

Copy the example before the first run:

```bash
cp backend/.env.example backend/.env
```

> Set `JWT_SECRET_KEY` to a strong random value before deploying anywhere
> non-local.

## Running the dev stack

From the repo root, using the [Makefile](../Makefile) targets:

```bash
make dev        # build + up with docker-compose.yml + docker-compose.dev.yml
make logs       # tail logs
make down       # stop the stack
make build      # rebuild the backend service
make lock       # regenerate poetry.lock inside the container
make test       # run pytest -v inside the backend container
```

The `docker-compose.dev.yml` override mounts `./backend:/app` and starts `uvicorn --reload`, so code changes hot-reload automatically.

## Database migrations

Alembic runs inside the backend container against the `db` Postgres service:

```bash
make migrate m="add events table"  # autogenerate revision + upgrade head
make upgrade                       # alembic upgrade head
make downgrade                     # alembic downgrade -1
```

When adding a new module with persistent state, import its ORM model in
[alembic/env.py](alembic/env.py) so autogenerate can detect the tables.

## Endpoints

| Method | Path                 | Auth                  | Description                                  |
|--------|----------------------|-----------------------|----------------------------------------------|
| GET    | `/api/health`        | —                     | Healthcheck                                  |
| POST   | `/api/auth/register` | —                     | Register a new user (JSON)                   |
| POST   | `/api/auth/login`    | —                     | Authenticate with email + password → JWT     |
| GET    | `/api/auth/me`       | Bearer                | Current user profile                         |
| POST   | `/api/events`        | Bearer (organizer/admin) | Create an event (status starts as `draft`) |
| GET    | `/api/events`        | —                     | List published events with pagination (`q`, `page`, `size`) |
| GET    | `/api/events/{id}`   | —                     | Event detail (any status); 404 if not found                  |
| PATCH  | `/api/events/{id}`   | Bearer (owner/admin)  | Update a draft event; 403/409/404 on guard failures          |
| POST   | `/api/events/{id}/publish` | Bearer (owner/admin) | Transition event to `published` (draft → published)     |
| POST   | `/api/events/{id}/cancel`  | Bearer (owner/admin) | Transition event to `cancelled` (draft/published → cancelled) |
| DELETE | `/api/events/{id}`         | Bearer (owner/admin) | Delete a draft or cancelled event; published returns 409      |

Interactive docs: <http://localhost:8000/api/docs>

## Observability

Every response carries an `x-request-id` header — generated by `RequestIdMiddleware` if the
client did not provide one — and the same id is injected into every JSON log line for the
request via a `ContextVar`. Logs are structured (one JSON object per line) on stdout.

```bash
curl -i http://localhost:8000/api/health
# x-request-id: 9b1f...                       (server-generated)

curl -i -H 'x-request-id: trace-abc' http://localhost:8000/api/health
# x-request-id: trace-abc                     (echoed back)
```
