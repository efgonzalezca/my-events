from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.modules.identity.domain.entities import User
from app.modules.identity.domain.exceptions import EmailAlreadyExists, UserNotFound
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

    def list_all(
        self, offset: int, limit: int
    ) -> tuple[list[User], int]:
        items_stmt = (
            select(UserORM)
            .order_by(UserORM.id.asc())
            .offset(offset)
            .limit(limit)
        )
        count_stmt = select(func.count()).select_from(UserORM)
        rows = self._s.exec(items_stmt).all()
        total = self._s.exec(count_stmt).one()
        return [to_domain(r) for r in rows], int(total)

    def update(self, user: User) -> User:
        orm = self._s.get(UserORM, user.id)
        if orm is None:
            raise UserNotFound(str(user.id))
        orm.role = user.role
        orm.is_active = user.is_active
        self._s.add(orm)
        self._s.commit()
        self._s.refresh(orm)
        return to_domain(orm)
