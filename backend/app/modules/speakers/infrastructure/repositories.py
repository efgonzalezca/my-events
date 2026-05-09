from sqlmodel import Session

from app.modules.speakers.domain.entities import Speaker
from app.modules.speakers.domain.repositories import SpeakerRepository
from app.modules.speakers.infrastructure.mappers import to_domain, to_orm


class SqlSpeakerRepository(SpeakerRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, speaker: Speaker) -> Speaker:
        orm = to_orm(speaker)
        self._s.add(orm)
        self._s.commit()
        self._s.refresh(orm)
        return to_domain(orm)