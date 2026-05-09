from typing import Annotated

from fastapi import Depends

from app.modules.identity.interfaces.http.deps import SessionDep
from app.modules.registrations.domain.repositories import RegistrationRepository
from app.modules.registrations.infrastructure.repositories import (
    SqlRegistrationRepository,
)


def get_registration_repo(s: SessionDep) -> RegistrationRepository:
    return SqlRegistrationRepository(s)


RegistrationRepoDep = Annotated[
    RegistrationRepository, Depends(get_registration_repo)
]