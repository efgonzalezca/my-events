from app.modules.events.application.dtos import CreateEventCmd, EventDTO
from app.modules.events.domain.entities import Event
from app.modules.events.domain.repositories import EventRepository
from app.modules.events.domain.value_objects import DateRange


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
