from dataclasses import dataclass
from datetime import datetime

from app.modules.events.domain.value_objects import EventStatus


@dataclass(frozen=True)
class CreateEventCmd:
    name: str
    description: str
    location: str
    starts_at: datetime
    ends_at: datetime
    capacity: int


@dataclass(frozen=True)
class UpdateEventCmd:
    name: str | None = None
    description: str | None = None
    location: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    capacity: int | None = None


@dataclass(frozen=True)
class EventDTO:
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


@dataclass(frozen=True)
class PaginatedEventsDTO:
    items: list[EventDTO]
    page: int
    size: int
    total: int
