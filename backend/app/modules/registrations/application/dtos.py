from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RegistrationDTO:
    id: int
    user_id: int
    event_id: int
    created_at: datetime