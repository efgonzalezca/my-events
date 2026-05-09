from fastapi import APIRouter, Depends, Query

from app.interfaces.http.auth import get_current_user, require_role
from app.modules.events.application.dtos import CreateEventCmd, UpdateEventCmd
from app.modules.events.application.use_cases import (
    cancel_event,
    create_event,
    delete_event,
    get_event,
    list_published_events,
    publish_event,
    update_event,
)
from app.modules.events.interfaces.http.deps import EventRepoDep
from app.modules.events.interfaces.http.schemas import (
    EventCreateRequest,
    EventResponse,
    EventUpdateRequest,
    PaginatedEventsResponse,
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


@router.get("", response_model=PaginatedEventsResponse)
def list_events_route(
    repo: EventRepoDep,
    q: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
) -> PaginatedEventsResponse:
    dto = list_published_events(q=q, page=page, size=size, repo=repo)
    return PaginatedEventsResponse(
        items=[EventResponse(**e.__dict__) for e in dto.items],
        page=dto.page,
        size=dto.size,
        total=dto.total,
    )


@router.get("/{event_id}", response_model=EventResponse)
def get_event_route(event_id: int, repo: EventRepoDep) -> EventResponse:
    dto = get_event(event_id, repo)
    return EventResponse(**dto.__dict__)


@router.patch("/{event_id}", response_model=EventResponse)
def update_event_route(
    event_id: int,
    req: EventUpdateRequest,
    repo: EventRepoDep,
    me: UserDTO = Depends(get_current_user),
) -> EventResponse:
    cmd = UpdateEventCmd(
        name=req.name,
        description=req.description,
        location=req.location,
        starts_at=req.starts_at,
        ends_at=req.ends_at,
        capacity=req.capacity,
    )
    dto = update_event(
        cmd,
        event_id=event_id,
        actor_id=me.id,
        actor_role=me.role,
        repo=repo,
    )
    return EventResponse(**dto.__dict__)


@router.post("/{event_id}/publish", response_model=EventResponse)
def publish_event_route(
    event_id: int,
    repo: EventRepoDep,
    me: UserDTO = Depends(get_current_user),
) -> EventResponse:
    dto = publish_event(
        event_id=event_id, actor_id=me.id, actor_role=me.role, repo=repo
    )
    return EventResponse(**dto.__dict__)


@router.post("/{event_id}/cancel", response_model=EventResponse)
def cancel_event_route(
    event_id: int,
    repo: EventRepoDep,
    me: UserDTO = Depends(get_current_user),
) -> EventResponse:
    dto = cancel_event(
        event_id=event_id, actor_id=me.id, actor_role=me.role, repo=repo
    )
    return EventResponse(**dto.__dict__)


@router.delete("/{event_id}", status_code=204)
def delete_event_route(
    event_id: int,
    repo: EventRepoDep,
    me: UserDTO = Depends(get_current_user),
) -> None:
    delete_event(
        event_id=event_id, actor_id=me.id, actor_role=me.role, repo=repo
    )