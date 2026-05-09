from sqlmodel import Session

from app.modules.events.domain.entities import Event
from app.modules.events.domain.repositories import EventRepository
from app.modules.events.infrastructure.mappers import to_domain, to_orm


class SqlEventRepository(EventRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, event: Event) -> Event:
        orm = to_orm(event)
        self._s.add(orm)
        self._s.commit()
        self._s.refresh(orm)
        return to_domain(orm)
