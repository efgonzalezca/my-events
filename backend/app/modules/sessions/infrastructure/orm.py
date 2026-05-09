from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class SessionORM(SQLModel, table=True):
    __tablename__ = "sessions"

    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="events.id", index=True)
    title: str = Field(max_length=255)
    description: str = Field(default="", max_length=4000)
    starts_at: datetime
    ends_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))