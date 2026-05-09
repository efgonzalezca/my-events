from fastapi import Depends, HTTPException

from app.modules.identity.application.dtos import UserDTO
from app.modules.identity.application.use_cases import get_me
from app.modules.identity.domain.entities import UserRole
from app.modules.identity.interfaces.http.deps import (
    CurrentUserId,
    UserRepoDep,
)


def get_current_user(user_id: CurrentUserId, repo: UserRepoDep) -> UserDTO:
    """Return the authenticated user's DTO; no role enforcement."""
    return get_me(user_id, repo)


def require_role(*roles: UserRole):
    """Factory of FastAPI dependencies that enforce role-based access."""

    def _dep(user_id: CurrentUserId, repo: UserRepoDep):
        dto = get_me(user_id, repo)
        if dto.role not in roles:
            raise HTTPException(
                status_code=403, detail="insufficient role"
            )
        return dto

    return Depends(_dep)
