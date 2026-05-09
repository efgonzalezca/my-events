from fastapi import APIRouter, Depends

from app.interfaces.http.auth import get_current_user
from app.modules.identity.application.dtos import UserDTO
from app.modules.registrations.application.use_cases import (
    cancel_registration,
    register_to_event,
)
from app.modules.registrations.interfaces.http.deps import RegistrationRepoDep
from app.modules.registrations.interfaces.http.schemas import RegistrationResponse

router = APIRouter()


@router.post(
    "/events/{event_id}/register",
    response_model=RegistrationResponse,
    status_code=201,
)
def register_route(
    event_id: int,
    repo: RegistrationRepoDep,
    me: UserDTO = Depends(get_current_user),
) -> RegistrationResponse:
    dto = register_to_event(user_id=me.id, event_id=event_id, repo=repo)
    return RegistrationResponse(**dto.__dict__)


@router.delete("/events/{event_id}/register", status_code=204)
def cancel_route(
    event_id: int,
    repo: RegistrationRepoDep,
    me: UserDTO = Depends(get_current_user),
) -> None:
    cancel_registration(user_id=me.id, event_id=event_id, repo=repo)