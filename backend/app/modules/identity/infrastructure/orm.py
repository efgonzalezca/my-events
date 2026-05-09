from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.modules.identity.domain.entities import UserRole


class UserORM(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)
    role: UserRole = Field(default=UserRole.attendee)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
