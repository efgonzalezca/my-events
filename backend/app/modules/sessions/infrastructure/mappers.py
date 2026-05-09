from datetime import datetime, timezone

from app.modules.events.domain.value_objects import DateRange
from app.modules.sessions.domain.entities import Session
from app.modules.sessions.infrastructure.orm import SessionORM


def _as_utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def to_domain(orm: SessionORM, speaker_ids: list[int] | None = None) -> Session:
    assert orm.id is not None
    return Session(
        id=orm.id,
        event_id=orm.event_id,
        title=orm.title,
        description=orm.description,
        schedule=DateRange(_as_utc(orm.starts_at), _as_utc(orm.ends_at)),
        speaker_ids=speaker_ids or [],
        created_at=_as_utc(orm.created_at),
    )


def to_orm(session: Session) -> SessionORM:
    return SessionORM(
        id=session.id,
        event_id=session.event_id,
        title=session.title,
        description=session.description,
        starts_at=session.schedule.start,
        ends_at=session.schedule.end,
        created_at=session.created_at,
    )