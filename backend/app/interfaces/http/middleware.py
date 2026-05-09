import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import request_id_ctx

logger = logging.getLogger("app.request")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        token = request_id_ctx.set(request_id)
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            logger.exception(
                "unhandled exception",
                extra={
                    "ctx_method": request.method,
                    "ctx_path": request.url.path,
                },
            )
            raise
        finally:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            request_id_ctx.reset(token)

        response.headers["x-request-id"] = request_id
        logger.info(
            "request",
            extra={
                "ctx_method": request.method,
                "ctx_path": request.url.path,
                "ctx_status": response.status_code,
                "ctx_elapsed_ms": elapsed_ms,
            },
        )
        return response
