from typing import Annotated

from fastapi import Depends

from app.modules.identity.interfaces.http.deps import SessionDep
from app.modules.sessions.domain.repositories import SessionRepository
from app.modules.sessions.infrastructure.repositories import SqlSessionRepository


def get_session_repo(s: SessionDep) -> SessionRepository:
    return SqlSessionRepository(s)


SessionRepoDep = Annotated[SessionRepository, Depends(get_session_repo)]