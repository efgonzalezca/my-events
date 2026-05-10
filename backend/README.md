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
│   │   ├── admin/
│   │   │   ├── application/             # use cases + DTOs (consumes UserRepository.list_all)
│   │   │   └── interfaces/http/         # /admin/users routes (require_role(admin) at router level)
│   │   ├── events/
│   │   │   ├── domain/                  # Event entity, status machine, value objects, errors
│   │   │   ├── application/             # use cases + DTOs
│   │   │   ├── infrastructure/          # SQLModel ORM, mappers, SqlEventRepository
│   │   │   └── interfaces/http/         # routes, schemas, FastAPI deps
│   │   ├── identity/
│   │   │   ├── domain/                  # entities, value objects, repo Protocols, errors
│   │   │   ├── application/             # use cases + DTOs
│   │   │   ├── infrastructure/          # SQLModel ORM, mappers, SqlUserRepository
│   │   │   └── interfaces/http/         # routes, schemas, FastAPI deps
│   │   ├── registrations/
│   │   │   ├── domain/                  # Registration entity, errors
│   │   │   ├── application/             # use cases + DTOs
│   │   │   ├── infrastructure/          # ORM (UNIQUE user_id+event_id), mappers, atomic try_register
│   │   │   └── interfaces/http/         # routes, schemas, FastAPI deps
│   │   ├── sessions/
│   │   │   ├── domain/                  # Session entity, SchedulePolicy, errors
│   │   │   ├── application/             # use cases + DTOs (consumes EventScheduleReader port)
│   │   │   ├── infrastructure/          # SQLModel ORM, mappers, SqlSessionRepository
│   │   │   └── interfaces/http/         # routes, schemas, FastAPI deps
│   │   └── speakers/
│   │       ├── domain/                  # Speaker entity, repo Protocol
│   │       ├── application/             # use cases + DTOs
│   │       ├── infrastructure/          # SQLModel ORM, mappers, SqlSpeakerRepository
│   │       └── interfaces/http/         # routes, schemas, FastAPI deps
│   ├── shared/
│   │   ├── application/ports/auth.py    # PasswordHasher / TokenService Protocols
│   │   ├── domain/exceptions.py         # DomainError base
│   │   └── infrastructure/
│   │       ├── db.py                    # engine + session_scope
│   │       └── security/                # BcryptHasher, JwtTokenService
│   └── main.py                          # create_app() + /api APIRouter wiring
├── scripts/
│   ├── seed.py                          # populate the DB with demo data
│   └── clean.py                         # TRUNCATE ... RESTART IDENTITY CASCADE
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
| `CORS_ORIGINS`                | `http://localhost:5173,http://localhost:3000,http://localhost:4200` (CSV) |

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
make seed       # populate the database with demo data
make clean-db   # truncate every domain table (preserves alembic_version)
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

## Demo data

[scripts/seed.py](scripts/seed.py) populates an empty database with realistic
data so the frontend has something to render. Run it once after `make dev` (and
any time you want a fresh dataset, after `make clean-db`):

```bash
make clean-db   # truncate domain tables (preserves alembic_version)
make seed       # load users, speakers, events, sessions, registrations
```

What gets created:

| Entity | Count | Detail |
|--------|-------|--------|
| Users | 13 | 1 admin, 4 organizers, 8 attendees — all with password `Test1234$` |
| Speakers | 6 | Ada Lovelace, Grace Hopper, Linus Torvalds, Guido van Rossum, Brendan Eich, Margaret Hamilton |
| Events | 13 | 4 past published + 5 future published + 3 draft + 1 cancelled |
| Sessions | 23 | 2 per past event, 3 per future published event, none on drafts/cancelled |
| Speaker links | 23 | One speaker per session, rotating through the pool |
| Registrations | 38 | Distributed across the 9 published events |

Demo logins (all share the same password):

```
admin@miseventos.com     (admin)
org1..org4@miseventos.com (organizer)
att1..att8@miseventos.com (attendee)
```

The seed script aborts if the `users` table is not empty, so always run
`make clean-db` first if you want to re-seed.

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
| POST   | `/api/speakers`            | Bearer (organizer/admin) | Create a speaker                                          |
| GET    | `/api/speakers`            | —                     | List speakers with pagination (`q`, `page`, `size`)              |
| GET    | `/api/speakers/{id}`       | —                     | Speaker detail; 404 `SPEAKER_NOT_FOUND` if missing                |
| PATCH  | `/api/speakers/{id}`       | Bearer (organizer/admin) | Update speaker fields (all optional)                           |
| DELETE | `/api/speakers/{id}`       | Bearer (organizer/admin) | Delete a speaker; 204                                          |
| POST   | `/api/events/{id}/sessions` | Bearer (organizer/admin) | Create a session inside the event range; 409 on out-of-range or schedule conflict |
| GET    | `/api/events/{id}/sessions` | —                     | List sessions of the event; 404 `EVENT_NOT_FOUND` if the event is missing       |
| GET    | `/api/sessions/{id}`        | —                     | Session detail; 404 `SESSION_NOT_FOUND` if missing                              |
| PATCH  | `/api/sessions/{id}`        | Bearer (organizer/admin) | Update session fields; revalidates fits_in and overlap if schedule changes   |
| DELETE | `/api/sessions/{id}`        | Bearer (organizer/admin) | Delete a session; 204                                                        |
| POST   | `/api/sessions/{sid}/speakers/{spid}` | Bearer (organizer/admin) | Link speaker to session; 404 if speaker missing, 409 if already linked |
| DELETE | `/api/sessions/{sid}/speakers/{spid}` | Bearer (organizer/admin) | Unlink speaker from session; 204; 404 if not linked                  |
| POST   | `/api/events/{id}/register` | Bearer                | Register the authenticated user; 409 on `NOT_PUBLISHED`/`EVENT_FULL`/`ALREADY_REGISTERED` |
| DELETE | `/api/events/{id}/register` | Bearer                | Cancel the authenticated user's registration; 204; 404 `REGISTRATION_NOT_FOUND` if absent |
| GET    | `/api/me/registrations`     | Bearer                | List the authenticated user's registrations with embedded event summary       |
| GET    | `/api/admin/users`          | Bearer (admin)        | List users with pagination (`page`, `size`)                                   |
| GET    | `/api/admin/users/{id}`     | Bearer (admin)        | User detail; 404 `USER_NOT_FOUND` if missing                                  |
| PATCH  | `/api/admin/users/{id}/role`   | Bearer (admin)     | Change a user's role; 409 `CANNOT_MODIFY_SELF` when targeting the caller        |
| PATCH  | `/api/admin/users/{id}/active` | Bearer (admin)     | Activate or deactivate a user; 409 `CANNOT_MODIFY_SELF` when targeting the caller |

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
