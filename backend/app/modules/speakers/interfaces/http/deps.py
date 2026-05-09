from typing import Annotated

from fastapi import Depends

from app.modules.identity.interfaces.http.deps import SessionDep
from app.modules.speakers.application.ports import SpeakerExistsReader
from app.modules.speakers.domain.repositories import SpeakerRepository
from app.modules.speakers.infrastructure.repositories import SqlSpeakerRepository
from app.modules.speakers.infrastructure.speaker_reader import (
    SqlSpeakerExistsReader,
)


def get_speaker_repo(s: SessionDep) -> SpeakerRepository:
    return SqlSpeakerRepository(s)


def get_speaker_exists_reader(s: SessionDep) -> SpeakerExistsReader:
    return SqlSpeakerExistsReader(s)


SpeakerRepoDep = Annotated[SpeakerRepository, Depends(get_speaker_repo)]
SpeakerExistsReaderDep = Annotated[
    SpeakerExistsReader, Depends(get_speaker_exists_reader)
]