from datetime import datetime, timezone

from app.modules.registrations.domain.entities import Registration
from app.modules.registrations.infrastructure.orm import RegistrationORM


def _as_utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def to_domain(orm: RegistrationORM) -> Registration:
    assert orm.id is not None
    return Registration(
        id=orm.id,
        user_id=orm.user_id,
        event_id=orm.event_id,
        created_at=_as_utc(orm.created_at),
    )