# My Events - Backend

REST API built with FastAPI on Python 3.12, packaged in Docker for development.

## Stack

- **Python** 3.12 (slim) + **Poetry** 2.4.0
- **FastAPI** 0.115.6 / **Uvicorn** 0.32.1 (standard, with `--reload` in dev)
- **Pydantic** 2.10.3 + **pydantic-settings** 2.7.0 for environment-based configuration
- **Pytest** 8.3.4 + **httpx** 0.28.1 (`dev` group)

## Layout

```
backend/
├── app/
│   ├── core/
│   │   └── config.py          # Settings (BaseSettings) loaded from .env
│   ├── interfaces/
│   │   └── http/
│   │       └── routes/
│   │           └── health.py  # GET /api/health
│   └── main.py                # create_app() + /api APIRouter wiring
├── Dockerfile                 # multi-stage: base → development
├── entrypoint.sh
├── pyproject.toml
└── poetry.lock
```

## Configuration

Environment variables (see [.env.example](.env.example)):

| Variable      | Default         |
|---------------|-----------------|
| `APP_NAME`    | `My Events API` |
| `ENVIRONMENT` | `development`   |
| `DEBUG`       | `false`         |
| `API_PREFIX`  | `/api`          |
| `HOST`        | `0.0.0.0`       |
| `PORT`        | `8000`          |

Copy the example before the first run:

```bash
cp backend/.env.example backend/.env
```

## Running the dev stack

From the repo root, using the [Makefile](../Makefile) targets:

```bash
make dev      # build + up with docker-compose.yml + docker-compose.dev.yml
make logs     # tail logs
make down     # stop the stack
make build    # rebuild the backend service
make lock     # regenerate poetry.lock inside the container
```

The `docker-compose.dev.yml` override mounts `./backend:/app` and starts `uvicorn --reload`, so code changes hot-reload automatically.

## Endpoints

| Method | Path          | Description |
|--------|---------------|-------------|
| GET    | `/api/health` | Healthcheck |

Interactive docs: <http://localhost:8000/docs>
