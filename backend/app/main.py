from fastapi import APIRouter, FastAPI

from app.core.config import settings
from app.core.logging import configure_logging
from app.interfaces.http.error_handlers import install_error_handlers
from app.interfaces.http.middleware import RequestIdMiddleware


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json"
    )

    install_error_handlers(app)
    app.add_middleware(RequestIdMiddleware)

    api = APIRouter(prefix=settings.api_prefix)

    from app.interfaces.http.routes import health
    from app.modules.events.interfaces.http.routes import router as events_router
    from app.modules.identity.interfaces.http.routes import router as identity_router
    from app.modules.sessions.interfaces.http.routes import router as sessions_router
    from app.modules.speakers.interfaces.http.routes import router as speakers_router

    api.include_router(health.router, tags=["health"])
    api.include_router(identity_router, prefix="/auth", tags=["auth"])
    api.include_router(events_router, prefix="/events", tags=["events"])
    api.include_router(speakers_router, prefix="/speakers", tags=["speakers"])
    api.include_router(sessions_router, tags=["sessions"])
    app.include_router(api)
    return app


app = create_app()
