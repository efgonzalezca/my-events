from typing import Annotated

from fastapi import Depends

from app.modules.events.application.ports import (
    EventReader,
    EventScheduleReader,
    EventSummaryReader,
)
from app.modules.events.domain.repositories import EventRepository
from app.modules.events.infrastructure.event_reader import (
    SqlEventReader,
    SqlEventScheduleReader,
    SqlEventSummaryReader,
)
from app.modules.events.infrastructure.repositories import SqlEventRepository
from app.modules.identity.interfaces.http.deps import SessionDep


def get_event_repo(s: SessionDep) -> EventRepository:
    return SqlEventRepository(s)


def get_event_schedule_reader(s: SessionDep) -> EventScheduleReader:
    return SqlEventScheduleReader(s)


def get_event_reader(s: SessionDep) -> EventReader:
    return SqlEventReader(s)


def get_event_summary_reader(s: SessionDep) -> EventSummaryReader:
    return SqlEventSummaryReader(s)


EventRepoDep = Annotated[EventRepository, Depends(get_event_repo)]
EventScheduleReaderDep = Annotated[
    EventScheduleReader, Depends(get_event_schedule_reader)
]
EventReaderDep = Annotated[EventReader, Depends(get_event_reader)]
EventSummaryReaderDep = Annotated[
    EventSummaryReader, Depends(get_event_summary_reader)
]
