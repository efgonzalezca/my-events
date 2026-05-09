from datetime import datetime

from pydantic import BaseModel


class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    created_at: datetime


class EventSummaryResponse(BaseModel):
    id: int
    name: str
    location: str
    starts_at: datetime
    ends_at: datetime
    capacity: int
    registered_count: int
    status: str


class MyRegistrationResponse(BaseModel):
    registration_id: int
    registered_at: datetime
    event: EventSummaryResponse