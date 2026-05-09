from typing import Annotated

from fastapi import Depends

from app.modules.events.domain.repositories import EventRepository
from app.modules.events.infrastructure.repositories import SqlEventRepository
from app.modules.identity.interfaces.http.deps import SessionDep


def get_event_repo(s: SessionDep) -> EventRepository:
    return SqlEventRepository(s)


EventRepoDep = Annotated[EventRepository, Depends(get_event_repo)]
