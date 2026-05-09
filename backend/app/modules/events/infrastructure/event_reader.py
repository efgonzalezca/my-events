from datetime import datetime, timezone

from sqlmodel import Session

from app.modules.events.application.ports import EventReader, EventScheduleReader
from app.modules.events.domain.exceptions import EventNotFound
from app.modules.events.infrastructure.orm import EventORM


def _as_utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


class SqlEventScheduleReader(EventScheduleReader):
    def __init__(self, session: Session) -> None:
        self._s = session

    def get_schedule(self, event_id: int) -> tuple[datetime, datetime]:
        orm = self._s.get(EventORM, event_id)
        if orm is None:
            raise EventNotFound(str(event_id))
        return _as_utc(orm.starts_at), _as_utc(orm.ends_at)


class SqlEventReader(EventReader):
    def __init__(self, session: Session) -> None:
        self._s = session

    def exists(self, event_id: int) -> bool:
        return self._s.get(EventORM, event_id) is not None