from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from app.modules.identity.domain.value_objects import Email


class UserRole(str, Enum):
    admin = "admin"
    organizer = "organizer"
    attendee = "attendee"


@dataclass
class User:
    id: int | None
    email: Email
    full_name: str
    password_hash: str
    role: UserRole = UserRole.attendee
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def change_role(self, role: UserRole) -> None:
        self.role = role

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False
