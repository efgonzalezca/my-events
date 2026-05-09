from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class RegistrationORM(SQLModel, table=True):
    __tablename__ = "registrations"
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_registrations_user_event"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    event_id: int = Field(foreign_key="events.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))