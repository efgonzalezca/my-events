from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.modules.identity.domain.entities import User
from app.modules.identity.domain.exceptions import EmailAlreadyExists
from app.modules.identity.domain.repositories import UserRepository
from app.modules.identity.domain.value_objects import Email
from app.modules.identity.infrastructure.mappers import to_domain, to_orm
from app.modules.identity.infrastructure.orm import UserORM


class SqlUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def get_by_id(self, user_id: int) -> User | None:
        orm = self._s.get(UserORM, user_id)
        return to_domain(orm) if orm else None

    def get_by_email(self, email: Email) -> User | None:
        orm = self._s.exec(
            select(UserORM).where(UserORM.email == email.value)
        ).first()
        return to_domain(orm) if orm else None

    def add(self, user: User) -> User:
        orm = to_orm(user)
        self._s.add(orm)
        try:
            self._s.commit()
        except IntegrityError:
            self._s.rollback()
            raise EmailAlreadyExists(user.email.value)
        self._s.refresh(orm)
        return to_domain(orm)
