from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.modules.events.domain.value_objects import DateRange


@dataclass
class Session:
    id: int | None
    event_id: int
    title: str
    description: str
    schedule: DateRange
    speaker_ids: list[int] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))