from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.modules.identity.domain.repositories import UserRepository
from app.modules.identity.infrastructure.repositories import SqlUserRepository
from app.shared.application.ports.auth import PasswordHasher, TokenService
from app.shared.infrastructure.db import session_scope
from app.shared.infrastructure.security.bcrypt_hasher import BcryptHasher
from app.shared.infrastructure.security.jwt_service import JwtTokenService

bearer_scheme = HTTPBearer()


SessionDep = Annotated[Session, Depends(session_scope)]


def get_user_repo(s: SessionDep) -> UserRepository:
    return SqlUserRepository(s)


def get_hasher() -> PasswordHasher:
    return BcryptHasher()


def get_tokens() -> TokenService:
    return JwtTokenService()


UserRepoDep = Annotated[UserRepository, Depends(get_user_repo)]
HasherDep = Annotated[PasswordHasher, Depends(get_hasher)]
TokensDep = Annotated[TokenService, Depends(get_tokens)]


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    tokens: TokensDep,
) -> int:
    sub = tokens.decode(credentials.credentials)
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
