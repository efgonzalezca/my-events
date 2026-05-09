from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.events.domain.value_objects import EventStatus


class EventCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=4000)
    location: str = Field(default="", max_length=255)
    starts_at: datetime
    ends_at: datetime
    capacity: int = Field(ge=1, le=1_000_000)


class EventResponse(BaseModel):
    id: int
    name: str
    description: str
    location: str
    starts_at: datetime
    ends_at: datetime
    capacity: int
    registered_count: int
    status: EventStatus
    organizer_id: int
