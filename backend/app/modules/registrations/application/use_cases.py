from app.modules.events.application.ports import EventSummaryReader
from app.modules.registrations.application.dtos import (
    MyRegistrationDTO,
    RegistrationDTO,
)
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


def cancel_registration(
    user_id: int, event_id: int, repo: RegistrationRepository
) -> None:
    repo.cancel(user_id, event_id)


def list_my_registrations(
    user_id: int,
    repo: RegistrationRepository,
    summary_reader: EventSummaryReader,
) -> list[MyRegistrationDTO]:
    regs = repo.list_by_user(user_id)
    if not regs:
        return []
    summaries = summary_reader.get_summaries([r.event_id for r in regs])
    summary_by_id = {s.id: s for s in summaries}
    return [
        MyRegistrationDTO(
            registration_id=r.id,
            registered_at=r.created_at,
            event=summary_by_id[r.event_id],
        )
        for r in regs
        if r.event_id in summary_by_id
    ]