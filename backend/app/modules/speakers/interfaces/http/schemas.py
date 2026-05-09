from pydantic import BaseModel, Field


class SpeakerCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    bio: str = Field(default="", max_length=4000)
    photo_url: str = Field(default="", max_length=500)


class SpeakerResponse(BaseModel):
    id: int
    name: str
    bio: str
    photo_url: str