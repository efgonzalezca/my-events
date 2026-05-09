from fastapi import APIRouter, FastAPI

from app.core.config import settings
from app.interfaces.http.error_handlers import install_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json"
    )

    install_error_handlers(app)

    api = APIRouter(prefix=settings.api_prefix)

    from app.interfaces.http.routes import health
    from app.modules.identity.interfaces.http.routes import router as identity_router

    api.include_router(health.router, tags=["health"])
    api.include_router(identity_router, prefix="/auth", tags=["auth"])
    app.include_router(api)
    return app


app = create_app()
