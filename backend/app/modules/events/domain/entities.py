from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.modules.events.domain.exceptions import InvalidStatusTransition
from app.modules.events.domain.value_objects import DateRange, EventStatus


_ALLOWED_TRANSITIONS: dict[EventStatus, set[EventStatus]] = {
    EventStatus.draft: {EventStatus.published, EventStatus.cancelled},
    EventStatus.published: {EventStatus.cancelled},
    EventStatus.cancelled: set(),
}


@dataclass
class Event:
    id: int | None
    name: str
    description: str
    location: str
    schedule: DateRange
    capacity: int
    organizer_id: int
    registered_count: int = 0
    status: EventStatus = EventStatus.draft
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def transition_to(self, new: EventStatus) -> None:
        if new not in _ALLOWED_TRANSITIONS[self.status]:
            raise InvalidStatusTransition(f"{self.status.value} -> {new.value}")
        self.status = new

    def is_modifiable(self) -> bool:
        return self.status == EventStatus.draft

    def has_capacity(self) -> bool:
        return self.registered_count < self.capacity
