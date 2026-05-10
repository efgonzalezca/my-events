from typing import Protocol

from app.modules.identity.domain.entities import User
from app.modules.identity.domain.value_objects import Email


class UserRepository(Protocol):
    def get_by_id(self, user_id: int) -> User | None: ...
    def get_by_email(self, email: Email) -> User | None: ...
    def add(self, user: User) -> User: ...
    def list_all(
        self, offset: int, limit: int
    ) -> tuple[list[User], int]:
        """Return (items, total) ordered by id ascending."""
        ...
