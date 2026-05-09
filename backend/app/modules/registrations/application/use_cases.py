from app.modules.registrations.application.dtos import RegistrationDTO
from app.modules.registrations.domain.entities import Registration
from app.modules.registrations.domain.repositories import RegistrationRepository


def to_dto(reg: Registration) -> RegistrationDTO:
    assert reg.id is not None
    return RegistrationDTO(
        id=reg.id,
        user_id=reg.user_id,
        event_id=reg.event_id,
        created_at=reg.created_at,
    )


def register_to_event(
    user_id: int, event_id: int, repo: RegistrationRepository
) -> RegistrationDTO:
    return to_dto(repo.try_register(user_id, event_id))