from app.modules.events.domain.entities import Event
from app.modules.events.domain.value_objects import DateRange
from app.modules.events.infrastructure.orm import EventORM


def to_domain(orm: EventORM) -> Event:
    assert orm.id is not None
    return Event(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        location=orm.location,
        schedule=DateRange(orm.starts_at, orm.ends_at),
        capacity=orm.capacity,
        organizer_id=orm.organizer_id,
        registered_count=orm.registered_count,
        status=orm.status,
        created_at=orm.created_at,
    )


def to_orm(event: Event) -> EventORM:
    return EventORM(
        id=event.id,
        name=event.name,
        description=event.description,
        location=event.location,
        starts_at=event.schedule.start,
        ends_at=event.schedule.end,
        capacity=event.capacity,
        registered_count=event.registered_count,
        status=event.status,
        organizer_id=event.organizer_id,
        created_at=event.created_at,
    )
