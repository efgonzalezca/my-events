from datetime import datetime

from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=4000)
    starts_at: datetime
    ends_at: datetime


class SessionResponse(BaseModel):
    id: int
    event_id: int
    title: str
    description: str
    starts_at: datetime
    ends_at: datetime
    speaker_ids: list[int]