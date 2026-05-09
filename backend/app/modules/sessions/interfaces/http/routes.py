from fastapi import APIRouter

from app.interfaces.http.auth import require_role
from app.modules.events.interfaces.http.deps import EventScheduleReaderDep
from app.modules.identity.application.dtos import UserDTO
from app.modules.identity.domain.entities import UserRole
from app.modules.sessions.application.dtos import CreateSessionCmd
from app.modules.sessions.application.use_cases import create_session
from app.modules.sessions.interfaces.http.deps import SessionRepoDep
from app.modules.sessions.interfaces.http.schemas import (
    SessionCreateRequest,
    SessionResponse,
)

router = APIRouter()


@router.post(
    "/events/{event_id}/sessions",
    response_model=SessionResponse,
    status_code=201,
)
def create_session_route(
    event_id: int,
    req: SessionCreateRequest,
    repo: SessionRepoDep,
    schedule_reader: EventScheduleReaderDep,
    _me: UserDTO = require_role(UserRole.organizer, UserRole.admin),
) -> SessionResponse:
    cmd = CreateSessionCmd(
        title=req.title,
        description=req.description,
        starts_at=req.starts_at,
        ends_at=req.ends_at,
    )
    dto = create_session(
        cmd, event_id=event_id, repo=repo, schedule_reader=schedule_reader
    )
    return SessionResponse(**dto.__dict__)