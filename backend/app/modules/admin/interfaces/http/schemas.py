from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.modules.identity.domain.entities import UserRole


class AdminUserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class PaginatedAdminUsersResponse(BaseModel):
    items: list[AdminUserResponse]
    page: int
    size: int
    total: int


class ChangeRoleRequest(BaseModel):
    role: UserRole


class SetActiveRequest(BaseModel):
    is_active: bool