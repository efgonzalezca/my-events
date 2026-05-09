from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.modules.events.domain.exceptions import EventNotFound
from app.modules.events.domain.value_objects import EventStatus
from app.modules.events.infrastructure.orm import EventORM
from app.modules.registrations.domain.entities import Registration
from app.modules.registrations.domain.exceptions import (
    AlreadyRegistered,
    EventFull,
    NotPublished,
    RegistrationNotFound,
)
from app.modules.registrations.domain.repositories import RegistrationRepository
from app.modules.registrations.infrastructure.mappers import to_domain
from app.modules.registrations.infrastructure.orm import RegistrationORM


class SqlRegistrationRepository(RegistrationRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def try_register(self, user_id: int, event_id: int) -> Registration:
        stmt = (
            update(EventORM)
            .where(
                EventORM.id == event_id,
                EventORM.status == EventStatus.published,
                EventORM.registered_count < EventORM.capacity,
            )
            .values(registered_count=EventORM.registered_count + 1)
        )
        result = self._s.execute(stmt)

        if result.rowcount == 0:
            ev = self._s.get(EventORM, event_id)
            if ev is None:
                raise EventNotFound(str(event_id))
            if ev.status != EventStatus.published:
                raise NotPublished(str(event_id))
            raise EventFull(str(event_id))

        reg = RegistrationORM(user_id=user_id, event_id=event_id)
        self._s.add(reg)
        try:
            self._s.commit()
        except IntegrityError:
            self._s.rollback()
            raise AlreadyRegistered(f"{user_id}:{event_id}")

        self._s.refresh(reg)
        return to_domain(reg)

    def list_by_user(self, user_id: int) -> list[Registration]:
        rows = self._s.exec(
            select(RegistrationORM)
            .where(RegistrationORM.user_id == user_id)
            .order_by(RegistrationORM.created_at.desc())
        ).all()
        return [to_domain(r) for r in rows]

    def cancel(self, user_id: int, event_id: int) -> None:
        reg = self._s.exec(
            select(RegistrationORM).where(
                RegistrationORM.user_id == user_id,
                RegistrationORM.event_id == event_id,
            )
        ).first()
        if reg is None:
            raise RegistrationNotFound(f"{user_id}:{event_id}")

        self._s.delete(reg)
        self._s.execute(
            update(EventORM)
            .where(
                EventORM.id == event_id,
                EventORM.registered_count > 0,
            )
            .values(registered_count=EventORM.registered_count - 1)
        )
        self._s.commit()