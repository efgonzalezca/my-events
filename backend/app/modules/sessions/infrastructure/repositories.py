from sqlmodel import Session as DbSession
from sqlmodel import select

from app.modules.sessions.domain.entities import Session
from app.modules.sessions.domain.exceptions import SessionNotFound
from app.modules.sessions.domain.repositories import SessionRepository
from app.modules.sessions.infrastructure.mappers import to_domain, to_orm
from app.modules.sessions.infrastructure.orm import SessionORM


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
        return [to_domain(r) for r in rows]

    def get(self, session_id: int) -> Session:
        orm = self._s.get(SessionORM, session_id)
        if orm is None:
            raise SessionNotFound(str(session_id))
        return to_domain(orm)