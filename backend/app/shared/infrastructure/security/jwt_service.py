from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings
from app.shared.application.ports.auth import TokenService


class JwtTokenService(TokenService):
    def issue(self, subject: str | int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        payload = {"sub": str(subject), "exp": expire}
        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    def decode(self, token: str) -> str | None:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except InvalidTokenError:
            return None
        sub = payload.get("sub")
        return str(sub) if sub is not None else None
