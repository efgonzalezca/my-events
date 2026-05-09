from datetime import datetime
from typing import Protocol


class EventScheduleReader(Protocol):
    def get_schedule(self, event_id: int) -> tuple[datetime, datetime]:
        """Return (starts_at, ends_at) of the event; raise EventNotFound if missing."""
        ...