from sqlmodel import Session as DbSession
from sqlmodel import select

from app.modules.sessions.domain.entities import Session
from app.modules.sessions.domain.exceptions import (
    SessionNotFound,
    SpeakerAlreadyLinked,
    SpeakerNotLinked,
)
from app.modules.sessions.domain.repositories import SessionRepository
from app.modules.sessions.infrastructure.mappers import to_domain, to_orm
from app.modules.sessions.infrastructure.orm import SessionORM, SessionSpeakerLinkORM


class SqlSessionRepository(SessionRepository):
    def __init__(self, session: DbSession) -> None:
        self._s = session

    def add(self, session: Session) -> Session:
        orm = to_orm(session)
        self._s.add(orm)
        self._s.commit()
        self._s.refresh(orm)
        return to_domain(orm)

    def list_by_event(self, event_id: int) -> list[Session]:
        rows = self._s.exec(
            select(SessionORM)
            .where(SessionORM.event_id == event_id)
            .order_by(SessionORM.starts_at.asc())
        ).all()
        return [
            to_domain(r, speaker_ids=self.list_speaker_ids(r.id)) for r in rows
        ]

    def get(self, session_id: int) -> Session:
        orm = self._s.get(SessionORM, session_id)
        if orm is None:
            raise SessionNotFound(str(session_id))
        return to_domain(orm, speaker_ids=self.list_speaker_ids(session_id))

    def update(self, session: Session) -> Session:
        orm = self._s.get(SessionORM, session.id)
        if orm is None:
            raise SessionNotFound(str(session.id))
        orm.title = session.title
        orm.description = session.description
        orm.starts_at = session.schedule.start
        orm.ends_at = session.schedule.end
        self._s.add(orm)
        self._s.commit()
        self._s.refresh(orm)
        return to_domain(orm, speaker_ids=self.list_speaker_ids(orm.id))

    def delete(self, session_id: int) -> None:
        orm = self._s.get(SessionORM, session_id)
        if orm is None:
            raise SessionNotFound(str(session_id))
        self._s.delete(orm)
        self._s.commit()

    def link_speaker(self, session_id: int, speaker_id: int) -> None:
        if self._s.get(SessionORM, session_id) is None:
            raise SessionNotFound(str(session_id))
        if self._s.get(SessionSpeakerLinkORM, (session_id, speaker_id)) is not None:
            raise SpeakerAlreadyLinked(f"{session_id}:{speaker_id}")
        link = SessionSpeakerLinkORM(
            session_id=session_id, speaker_id=speaker_id
        )
        self._s.add(link)
        self._s.commit()

    def unlink_speaker(self, session_id: int, speaker_id: int) -> None:
        if self._s.get(SessionORM, session_id) is None:
            raise SessionNotFound(str(session_id))
        link = self._s.get(SessionSpeakerLinkORM, (session_id, speaker_id))
        if link is None:
            raise SpeakerNotLinked(f"{session_id}:{speaker_id}")
        self._s.delete(link)
        self._s.commit()

    def list_speaker_ids(self, session_id: int) -> list[int]:
        rows = self._s.exec(
            select(SessionSpeakerLinkORM.speaker_id)
            .where(SessionSpeakerLinkORM.session_id == session_id)
        ).all()
        return list(rows)