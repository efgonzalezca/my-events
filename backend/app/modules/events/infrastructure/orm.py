from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.modules.events.domain.value_objects import EventStatus


class EventORM(SQLModel, table=True):
    __tablename__ = "events"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    description: str = Field(default="", max_length=4000)
    location: str = Field(default="", max_length=255)
    starts_at: datetime
    ends_at: datetime
    capacity: int = Field(ge=0)
    registered_count: int = Field(default=0, ge=0)
    status: EventStatus = Field(default=EventStatus.draft, index=True)
    organizer_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
