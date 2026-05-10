from dataclasses import dataclass
from datetime import datetime

from app.modules.identity.domain.entities import UserRole


@dataclass(frozen=True)
class AdminUserDTO:
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


@dataclass(frozen=True)
class PaginatedAdminUsersDTO:
    items: list[AdminUserDTO]
    page: int
    size: int
    total: int