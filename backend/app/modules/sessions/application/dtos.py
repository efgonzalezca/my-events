from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateSessionCmd:
    title: str
    description: str
    starts_at: datetime
    ends_at: datetime


@dataclass(frozen=True)
class SessionDTO:
    id: int
    event_id: int
    title: str
    description: str
    starts_at: datetime
    ends_at: datetime
    speaker_ids: list[int]
