from app.modules.admin.application.dtos import (
    AdminUserDTO,
    PaginatedAdminUsersDTO,
)
from app.modules.identity.domain.entities import User
from app.modules.identity.domain.exceptions import UserNotFound
from app.modules.identity.domain.repositories import UserRepository


def to_dto(user: User) -> AdminUserDTO:
    assert user.id is not None
    return AdminUserDTO(
        id=user.id,
        email=user.email.value,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


def list_users(
    page: int, size: int, repo: UserRepository
) -> PaginatedAdminUsersDTO:
    offset = (page - 1) * size
    items, total = repo.list_all(offset=offset, limit=size)
    return PaginatedAdminUsersDTO(
        items=[to_dto(u) for u in items],
        page=page,
        size=size,
        total=total,
    )


def get_user(user_id: int, repo: UserRepository) -> AdminUserDTO:
    user = repo.get_by_id(user_id)
    if user is None:
        raise UserNotFound(str(user_id))
    return to_dto(user)