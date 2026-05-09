from typing import Annotated

from fastapi import Depends

from app.modules.identity.interfaces.http.deps import SessionDep
from app.modules.speakers.domain.repositories import SpeakerRepository
from app.modules.speakers.infrastructure.repositories import SqlSpeakerRepository


def get_speaker_repo(s: SessionDep) -> SpeakerRepository:
    return SqlSpeakerRepository(s)


SpeakerRepoDep = Annotated[SpeakerRepository, Depends(get_speaker_repo)]