from dataclasses import dataclass

from app.modules.identity.domain.entities import UserRole


@dataclass(frozen=True)
class RegisterUserCmd:
    email: str
    password: str
    full_name: str


@dataclass(frozen=True)
class LoginCmd:
    email: str
    password: str


@dataclass(frozen=True)
class UserDTO:
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool


@dataclass(frozen=True)
class TokenDTO:
    access_token: str
    token_type: str = "bearer"
