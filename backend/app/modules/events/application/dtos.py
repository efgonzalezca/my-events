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
