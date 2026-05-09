from dataclasses import dataclass


@dataclass(frozen=True)
class CreateSpeakerCmd:
    name: str
    bio: str
    photo_url: str


@dataclass(frozen=True)
class UpdateSpeakerCmd:
    name: str | None = None
    bio: str | None = None
    photo_url: str | None = None


@dataclass(frozen=True)
class SpeakerDTO:
    id: int
    name: str
    bio: str
    photo_url: str


@dataclass(frozen=True)
class PaginatedSpeakersDTO:
    items: list[SpeakerDTO]
    page: int
    size: int
    total: int