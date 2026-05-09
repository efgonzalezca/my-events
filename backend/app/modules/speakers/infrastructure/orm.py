from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class SpeakerORM(SQLModel, table=True):
    __tablename__ = "speakers"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    bio: str = Field(default="", max_length=4000)
    photo_url: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))