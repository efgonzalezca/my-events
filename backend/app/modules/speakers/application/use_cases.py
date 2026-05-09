from app.modules.speakers.application.dtos import CreateSpeakerCmd, SpeakerDTO
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