from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class EventScheduleReader(Protocol):
    def get_schedule(self, event_id: int) -> tuple[datetime, datetime]:
        """Return (starts_at, ends_at) of the event; raise EventNotFound if missing."""
        ...


class EventReader(Protocol):
    def exists(self, event_id: int) -> bool:
        """Return True if an event with this id exists."""
        ...


@dataclass(frozen=True)
class EventSummary:
    id: int
    name: str
    location: str
    starts_at: datetime
    ends_at: datetime
    capacity: int
    registered_count: int
    status: str


class EventSummaryReader(Protocol):
    def get_summaries(self, event_ids: list[int]) -> list[EventSummary]:
        """Return summaries for the requested ids; missing ids are omitted."""
        ...