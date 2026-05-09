from fastapi import APIRouter, FastAPI

from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    api = APIRouter(prefix=settings.api_prefix)

    from app.interfaces.http.routes import health

    api.include_router(health.router, tags=["health"])
    app.include_router(api)
    return app


app = create_app()
