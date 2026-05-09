from fastapi import APIRouter

from app.interfaces.http.auth import require_role
from app.modules.events.interfaces.http.deps import (
    EventReaderDep,
    EventScheduleReaderDep,
)
from app.modules.identity.application.dtos import UserDTO
from app.modules.identity.domain.entities import UserRole
from app.modules.sessions.application.dtos import (
    CreateSessionCmd,
    UpdateSessionCmd,
)
from app.modules.sessions.application.use_cases import (
    create_session,
    delete_session,
    get_session,
    list_sessions_of_event,
    update_session,
)
from app.modules.sessions.interfaces.http.deps import SessionRepoDep
from app.modules.sessions.interfaces.http.schemas import (
    SessionCreateRequest,
    SessionResponse,
    SessionUpdateRequest,
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


@router.get(
    "/events/{event_id}/sessions", response_model=list[SessionResponse]
)
def list_sessions_route(
    event_id: int,
    repo: SessionRepoDep,
    event_reader: EventReaderDep,
) -> list[SessionResponse]:
    items = list_sessions_of_event(event_id, repo=repo, event_reader=event_reader)
    return [SessionResponse(**s.__dict__) for s in items]


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session_route(
    session_id: int, repo: SessionRepoDep
) -> SessionResponse:
    dto = get_session(session_id, repo=repo)
    return SessionResponse(**dto.__dict__)


@router.patch("/sessions/{session_id}", response_model=SessionResponse)
def update_session_route(
    session_id: int,
    req: SessionUpdateRequest,
    repo: SessionRepoDep,
    schedule_reader: EventScheduleReaderDep,
    _me: UserDTO = require_role(UserRole.organizer, UserRole.admin),
) -> SessionResponse:
    cmd = UpdateSessionCmd(
        title=req.title,
        description=req.description,
        starts_at=req.starts_at,
        ends_at=req.ends_at,
    )
    dto = update_session(
        cmd, session_id=session_id, repo=repo, schedule_reader=schedule_reader
    )
    return SessionResponse(**dto.__dict__)


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session_route(
    session_id: int,
    repo: SessionRepoDep,
    _me: UserDTO = require_role(UserRole.organizer, UserRole.admin),
) -> None:
    delete_session(session_id, repo=repo)