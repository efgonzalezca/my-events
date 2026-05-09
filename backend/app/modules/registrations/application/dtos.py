from dataclasses import dataclass
from datetime import datetime

from app.modules.events.application.ports import EventSummary


@dataclass(frozen=True)
class RegistrationDTO:
    id: int
    user_id: int
    event_id: int
    created_at: datetime


@dataclass(frozen=True)
class MyRegistrationDTO:
    registration_id: int
    registered_at: datetime
    event: EventSummary