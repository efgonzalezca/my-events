from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Speaker:
    id: int | None
    name: str
    bio: str = ""
    photo_url: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))