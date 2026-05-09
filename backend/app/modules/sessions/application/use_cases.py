from app.modules.events.application.ports import EventReader, EventScheduleReader
from app.modules.events.domain.exceptions import EventNotFound
from app.modules.events.domain.value_objects import DateRange
from app.modules.sessions.application.dtos import (
    CreateSessionCmd,
    SessionDTO,
    UpdateSessionCmd,
)
from app.modules.sessions.domain.entities import Session
from app.modules.sessions.domain.exceptions import (
    SessionOutOfEventRange,
    SessionScheduleConflict,
)
from app.modules.sessions.domain.policies import SchedulePolicy
from app.modules.sessions.domain.repositories import SessionRepository
from app.modules.speakers.application.ports import SpeakerExistsReader
from app.modules.speakers.domain.exceptions import SpeakerNotFound


def to_dto(session: Session) -> SessionDTO:
    assert session.id is not None
    return SessionDTO(
        id=session.id,
        event_id=session.event_id,
        title=session.title,
        description=session.description,
        starts_at=session.schedule.start,
        ends_at=session.schedule.end,
        speaker_ids=list(session.speaker_ids),
    )


def create_session(
    cmd: CreateSessionCmd,
    event_id: int,
    repo: SessionRepository,
    schedule_reader: EventScheduleReader,
) -> SessionDTO:
    event_start, event_end = schedule_reader.get_schedule(event_id)
    event_range = DateRange(event_start, event_end)
    session_range = DateRange(cmd.starts_at, cmd.ends_at)

    if not SchedulePolicy.fits_in(session_range, event_range):
        raise SessionOutOfEventRange(str(event_id))

    existing = repo.list_by_event(event_id)
    if SchedulePolicy.overlaps_with(
        session_range, [s.schedule for s in existing]
    ):
        raise SessionScheduleConflict(str(event_id))

    session = Session(
        id=None,
        event_id=event_id,
        title=cmd.title,
        description=cmd.description,
        schedule=session_range,
    )
    return to_dto(repo.add(session))


def list_sessions_of_event(
    event_id: int, repo: SessionRepository, event_reader: EventReader
) -> list[SessionDTO]:
    if not event_reader.exists(event_id):
        raise EventNotFound(str(event_id))
    return [to_dto(s) for s in repo.list_by_event(event_id)]


def get_session(session_id: int, repo: SessionRepository) -> SessionDTO:
    return to_dto(repo.get(session_id))


def update_session(
    cmd: UpdateSessionCmd,
    session_id: int,
    repo: SessionRepository,
    schedule_reader: EventScheduleReader,
) -> SessionDTO:
    session = repo.get(session_id)

    if cmd.title is not None:
        session.title = cmd.title
    if cmd.description is not None:
        session.description = cmd.description

    schedule_changed = cmd.starts_at is not None or cmd.ends_at is not None
    if schedule_changed:
        new_start = cmd.starts_at if cmd.starts_at is not None else session.schedule.start
        new_end = cmd.ends_at if cmd.ends_at is not None else session.schedule.end
        new_range = DateRange(new_start, new_end)

        event_start, event_end = schedule_reader.get_schedule(session.event_id)
        if not SchedulePolicy.fits_in(new_range, DateRange(event_start, event_end)):
            raise SessionOutOfEventRange(str(session.event_id))

        others = [
            s for s in repo.list_by_event(session.event_id) if s.id != session_id
        ]
        if SchedulePolicy.overlaps_with(new_range, [s.schedule for s in others]):
            raise SessionScheduleConflict(str(session.event_id))

        session.schedule = new_range

    return to_dto(repo.update(session))


def delete_session(session_id: int, repo: SessionRepository) -> None:
    repo.delete(session_id)


def link_speaker_to_session(
    session_id: int,
    speaker_id: int,
    repo: SessionRepository,
    speaker_reader: SpeakerExistsReader,
) -> SessionDTO:
    if not speaker_reader.exists(speaker_id):
        raise SpeakerNotFound(str(speaker_id))
    repo.link_speaker(session_id, speaker_id)
    return to_dto(repo.get(session_id))


def unlink_speaker_from_session(
    session_id: int, speaker_id: int, repo: SessionRepository
) -> None:
    repo.unlink_speaker(session_id, speaker_id)