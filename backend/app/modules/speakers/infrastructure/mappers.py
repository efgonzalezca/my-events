from app.modules.speakers.domain.entities import Speaker
from app.modules.speakers.infrastructure.orm import SpeakerORM


def to_domain(orm: SpeakerORM) -> Speaker:
    assert orm.id is not None
    return Speaker(
        id=orm.id,
        name=orm.name,
        bio=orm.bio,
        photo_url=orm.photo_url,
        created_at=orm.created_at,
    )


def to_orm(speaker: Speaker) -> SpeakerORM:
    return SpeakerORM(
        id=speaker.id,
        name=speaker.name,
        bio=speaker.bio,
        photo_url=speaker.photo_url,
        created_at=speaker.created_at,
    )