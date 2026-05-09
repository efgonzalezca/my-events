from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Registration:
    id: int | None
    user_id: int
    event_id: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))