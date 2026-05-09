from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.shared.domain.exceptions import DomainError


ERROR_TO_HTTP: dict[str, int] = {
    "EMAIL_ALREADY_EXISTS": 409,
    "INVALID_CREDENTIALS": 401,
    "USER_NOT_FOUND": 404,
    "EVENT_NOT_FOUND": 404,
    "EVENT_NOT_OWNED": 403,
    "EVENT_NOT_MODIFIABLE": 409,
    "INVALID_STATUS_TRANSITION": 409,
}


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=ERROR_TO_HTTP.get(exc.code, 400),
        content={"detail": str(exc) or exc.code, "code": exc.code},
    )


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
