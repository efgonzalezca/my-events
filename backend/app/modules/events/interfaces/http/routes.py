from fastapi import APIRouter

from app.interfaces.http.auth import require_role
from app.modules.events.application.dtos import CreateEventCmd
from app.modules.events.application.use_cases import create_event
from app.modules.events.interfaces.http.deps import EventRepoDep
from app.modules.events.interfaces.http.schemas import (
    EventCreateRequest,
    EventResponse,
)
from app.modules.identity.application.dtos import UserDTO
from app.modules.identity.domain.entities import UserRole

router = APIRouter()


@router.post("", response_model=EventResponse, status_code=201)
def create_event_route(
    req: EventCreateRequest,
    repo: EventRepoDep,
    me: UserDTO = require_role(UserRole.organizer, UserRole.admin),
) -> EventResponse:
    cmd = CreateEventCmd(
        name=req.name,
        description=req.description,
        location=req.location,
        starts_at=req.starts_at,
        ends_at=req.ends_at,
        capacity=req.capacity,
    )
    dto = create_event(cmd, organizer_id=me.id, repo=repo)
    return EventResponse(**dto.__dict__)
