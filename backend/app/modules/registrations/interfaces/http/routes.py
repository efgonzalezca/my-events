from fastapi import APIRouter, Depends

from app.interfaces.http.auth import get_current_user
from app.modules.events.interfaces.http.deps import EventSummaryReaderDep
from app.modules.identity.application.dtos import UserDTO
from app.modules.registrations.application.use_cases import (
    cancel_registration,
    list_my_registrations,
    register_to_event,
)
from app.modules.registrations.interfaces.http.deps import RegistrationRepoDep
from app.modules.registrations.interfaces.http.schemas import (
    EventSummaryResponse,
    MyRegistrationResponse,
    RegistrationResponse,
)

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


@router.get("/me/registrations", response_model=list[MyRegistrationResponse])
def list_my_registrations_route(
    repo: RegistrationRepoDep,
    summary_reader: EventSummaryReaderDep,
    me: UserDTO = Depends(get_current_user),
) -> list[MyRegistrationResponse]:
    items = list_my_registrations(
        user_id=me.id, repo=repo, summary_reader=summary_reader
    )
    return [
        MyRegistrationResponse(
            registration_id=i.registration_id,
            registered_at=i.registered_at,
            event=EventSummaryResponse(**i.event.__dict__),
        )
        for i in items
    ]