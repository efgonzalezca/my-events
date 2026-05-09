from app.modules.speakers.application.dtos import (
    CreateSpeakerCmd,
    PaginatedSpeakersDTO,
    SpeakerDTO,
)
from app.modules.speakers.domain.entities import Speaker
from app.modules.speakers.domain.repositories import SpeakerRepository


def to_dto(speaker: Speaker) -> SpeakerDTO:
    assert speaker.id is not None
    return SpeakerDTO(
        id=speaker.id,
        name=speaker.name,
        bio=speaker.bio,
        photo_url=speaker.photo_url,
    )


def create_speaker(cmd: CreateSpeakerCmd, repo: SpeakerRepository) -> SpeakerDTO:
    speaker = Speaker(
        id=None,
        name=cmd.name,
        bio=cmd.bio,
        photo_url=cmd.photo_url,
    )
    return to_dto(repo.add(speaker))


def get_speaker(speaker_id: int, repo: SpeakerRepository) -> SpeakerDTO:
    return to_dto(repo.get(speaker_id))


def list_speakers(
    q: str | None, page: int, size: int, repo: SpeakerRepository
) -> PaginatedSpeakersDTO:
    offset = (page - 1) * size
    items, total = repo.list_all(q=q, offset=offset, limit=size)
    return PaginatedSpeakersDTO(
        items=[to_dto(s) for s in items],
        page=page,
        size=size,
        total=total,
    )