from dataclasses import asdict
from typing import Any

from app.core.config import settings
from app.modules.events.application.dtos import (
    CreateEventCmd,
    EventDTO,
    PaginatedEventsDTO,
    UpdateEventCmd,
)
from app.modules.events.domain.entities import Event
from app.modules.events.domain.exceptions import (
    CapacityBelowRegistered,
    EventNotModifiable,
    EventNotOwned,
)
from app.modules.events.domain.repositories import EventRepository
from app.modules.events.domain.value_objects import DateRange, EventStatus
from app.modules.identity.domain.entities import UserRole
from app.shared.application.cache_decorator import cached
from app.shared.application.ports.cache import CacheService


def to_dto(event: Event) -> EventDTO:
    assert event.id is not None
    return EventDTO(
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
    )


def create_event(
    cmd: CreateEventCmd,
    organizer_id: int,
    repo: EventRepository,
    cache: CacheService,
) -> EventDTO:
    event = Event(
        id=None,
        name=cmd.name,
        description=cmd.description,
        location=cmd.location,
        schedule=DateRange(cmd.starts_at, cmd.ends_at),
        capacity=cmd.capacity,
        organizer_id=organizer_id,
    )
    dto = to_dto(repo.add(event))
    cache.invalidate_prefix("events:")
    return dto


def get_event(event_id: int, repo: EventRepository) -> EventDTO:
    return to_dto(repo.get(event_id))


def update_event(
    cmd: UpdateEventCmd,
    event_id: int,
    actor_id: int,
    actor_role: UserRole,
    repo: EventRepository,
    cache: CacheService,
) -> EventDTO:
    event = repo.get(event_id)
    if actor_role != UserRole.admin and event.organizer_id != actor_id:
        raise EventNotOwned(str(event_id))
    if not event.is_modifiable():
        raise EventNotModifiable(str(event_id))

    if cmd.name is not None:
        event.name = cmd.name
    if cmd.description is not None:
        event.description = cmd.description
    if cmd.location is not None:
        event.location = cmd.location
    if cmd.starts_at is not None or cmd.ends_at is not None:
        new_start = cmd.starts_at if cmd.starts_at is not None else event.schedule.start
        new_end = cmd.ends_at if cmd.ends_at is not None else event.schedule.end
        event.schedule = DateRange(new_start, new_end)
    if cmd.capacity is not None:
        if cmd.capacity < event.registered_count:
            raise CapacityBelowRegistered(str(event_id))
        event.capacity = cmd.capacity

    dto = to_dto(repo.update(event))
    cache.invalidate_prefix("events:")
    return dto


def _transition(
    event_id: int,
    actor_id: int,
    actor_role: UserRole,
    repo: EventRepository,
    cache: CacheService,
    target: EventStatus,
) -> EventDTO:
    event = repo.get(event_id)
    if actor_role != UserRole.admin and event.organizer_id != actor_id:
        raise EventNotOwned(str(event_id))
    event.transition_to(target)
    dto = to_dto(repo.update(event))
    cache.invalidate_prefix("events:")
    return dto


def publish_event(
    event_id: int,
    actor_id: int,
    actor_role: UserRole,
    repo: EventRepository,
    cache: CacheService,
) -> EventDTO:
    return _transition(
        event_id, actor_id, actor_role, repo, cache, EventStatus.published
    )


def cancel_event(
    event_id: int,
    actor_id: int,
    actor_role: UserRole,
    repo: EventRepository,
    cache: CacheService,
) -> EventDTO:
    return _transition(
        event_id, actor_id, actor_role, repo, cache, EventStatus.cancelled
    )


def delete_event(
    event_id: int,
    actor_id: int,
    actor_role: UserRole,
    repo: EventRepository,
    cache: CacheService,
) -> None:
    event = repo.get(event_id)
    if actor_role != UserRole.admin and event.organizer_id != actor_id:
        raise EventNotOwned(str(event_id))
    if event.status not in (EventStatus.draft, EventStatus.cancelled):
        raise EventNotModifiable(str(event_id))
    repo.delete(event_id)
    cache.invalidate_prefix("events:")


@cached("events:list", ttl=settings.cache_ttl_seconds)
def list_published_events(
    q: str | None, page: int, size: int, repo: EventRepository
) -> dict[str, Any]:
    offset = (page - 1) * size
    items, total = repo.list_published(q=q, offset=offset, limit=size)
    return asdict(
        PaginatedEventsDTO(
            items=[to_dto(e) for e in items],
            page=page,
            size=size,
            total=total,
        )
    )