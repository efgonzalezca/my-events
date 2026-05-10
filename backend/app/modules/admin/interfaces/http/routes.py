from fastapi import APIRouter, Query

from app.interfaces.http.auth import require_role
from app.modules.admin.application.use_cases import get_user, list_users
from app.modules.admin.interfaces.http.schemas import (
    AdminUserResponse,
    PaginatedAdminUsersResponse,
)
from app.modules.identity.domain.entities import UserRole
from app.modules.identity.interfaces.http.deps import UserRepoDep

router = APIRouter(dependencies=[require_role(UserRole.admin)])


@router.get("/users", response_model=PaginatedAdminUsersResponse)
def list_users_route(
    repo: UserRepoDep,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> PaginatedAdminUsersResponse:
    dto = list_users(page=page, size=size, repo=repo)
    return PaginatedAdminUsersResponse(
        items=[AdminUserResponse(**u.__dict__) for u in dto.items],
        page=dto.page,
        size=dto.size,
        total=dto.total,
    )


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user_route(user_id: int, repo: UserRepoDep) -> AdminUserResponse:
    dto = get_user(user_id, repo)
    return AdminUserResponse(**dto.__dict__)