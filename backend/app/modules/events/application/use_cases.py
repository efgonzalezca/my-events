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
    cmd: CreateEventCmd, organizer_id: int, repo: EventRepository
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
    return to_dto(repo.add(event))


def get_event(event_id: int, repo: EventRepository) -> EventDTO:
    return to_dto(repo.get(event_id))


def update_event(
    cmd: UpdateEventCmd,
    event_id: int,
    actor_id: int,
    actor_role: UserRole,
    repo: EventRepository,
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

    return to_dto(repo.update(event))


def _transition(
    event_id: int,
    actor_id: int,
    actor_role: UserRole,
    repo: EventRepository,
    target: EventStatus,
) -> EventDTO:
    event = repo.get(event_id)
    if actor_role != UserRole.admin and event.organizer_id != actor_id:
        raise EventNotOwned(str(event_id))
    event.transition_to(target)
    return to_dto(repo.update(event))


def publish_event(
    event_id: int, actor_id: int, actor_role: UserRole, repo: EventRepository
) -> EventDTO:
    return _transition(event_id, actor_id, actor_role, repo, EventStatus.published)


def cancel_event(
    event_id: int, actor_id: int, actor_role: UserRole, repo: EventRepository
) -> EventDTO:
    return _transition(event_id, actor_id, actor_role, repo, EventStatus.cancelled)


def delete_event(
    event_id: int, actor_id: int, actor_role: UserRole, repo: EventRepository
) -> None:
    event = repo.get(event_id)
    if actor_role != UserRole.admin and event.organizer_id != actor_id:
        raise EventNotOwned(str(event_id))
    if event.status not in (EventStatus.draft, EventStatus.cancelled):
        raise EventNotModifiable(str(event_id))
    repo.delete(event_id)


def list_published_events(
    q: str | None, page: int, size: int, repo: EventRepository
) -> PaginatedEventsDTO:
    offset = (page - 1) * size
    items, total = repo.list_published(q=q, offset=offset, limit=size)
    return PaginatedEventsDTO(
        items=[to_dto(e) for e in items],
        page=page,
        size=size,
        total=total,
    )
