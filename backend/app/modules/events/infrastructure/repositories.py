from sqlalchemy import func
from sqlmodel import Session, select

from app.modules.events.domain.entities import Event
from app.modules.events.domain.exceptions import EventNotFound
from app.modules.events.domain.repositories import EventRepository
from app.modules.events.domain.value_objects import EventStatus
from app.modules.events.infrastructure.mappers import to_domain, to_orm
from app.modules.events.infrastructure.orm import EventORM


class SqlEventRepository(EventRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, event: Event) -> Event:
        orm = to_orm(event)
        self._s.add(orm)
        self._s.commit()
        self._s.refresh(orm)
        return to_domain(orm)

    def list_published(
        self, q: str | None, offset: int, limit: int
    ) -> tuple[list[Event], int]:
        filters = [EventORM.status == EventStatus.published]
        if q:
            filters.append(EventORM.name.ilike(f"%{q}%"))

        items_stmt = (
            select(EventORM)
            .where(*filters)
            .order_by(EventORM.starts_at.asc())
            .offset(offset)
            .limit(limit)
        )
        count_stmt = select(func.count()).select_from(EventORM).where(*filters)

        rows = self._s.exec(items_stmt).all()
        total = self._s.exec(count_stmt).one()
        return [to_domain(r) for r in rows], int(total)

    def get(self, event_id: int) -> Event:
        orm = self._s.get(EventORM, event_id)
        if orm is None:
            raise EventNotFound(str(event_id))
        return to_domain(orm)