from app.modules.identity.application.dtos import (
    LoginCmd,
    RegisterUserCmd,
    TokenDTO,
    UserDTO,
)
from app.modules.identity.domain.entities import User, UserRole
from app.modules.identity.domain.exceptions import (
    EmailAlreadyExists,
    InvalidCredentials,
    UserNotFound,
)
from app.modules.identity.domain.repositories import UserRepository
from app.modules.identity.domain.value_objects import Email
from app.shared.application.ports.auth import PasswordHasher, TokenService


def to_dto(user: User) -> UserDTO:
    assert user.id is not None
    return UserDTO(
        id=user.id,
        email=user.email.value,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )


def register_user(
    cmd: RegisterUserCmd,
    repo: UserRepository,
    hasher: PasswordHasher,
) -> UserDTO:
    email = Email(cmd.email)
    if repo.get_by_email(email) is not None:
        raise EmailAlreadyExists(cmd.email)
    user = User(
        id=None,
        email=email,
        full_name=cmd.full_name,
        password_hash=hasher.hash(cmd.password),
        role=UserRole.attendee,
    )
    return to_dto(repo.add(user))


def login(
    cmd: LoginCmd,
    repo: UserRepository,
    hasher: PasswordHasher,
    tokens: TokenService,
) -> TokenDTO:
    user = repo.get_by_email(Email(cmd.email))
    if user is None or not user.is_active:
        raise InvalidCredentials()
    if not hasher.verify(cmd.password, user.password_hash):
        raise InvalidCredentials()
    assert user.id is not None
    return TokenDTO(access_token=tokens.issue(user.id))


def get_me(user_id: int, repo: UserRepository) -> UserDTO:
    user = repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise UserNotFound()
    return to_dto(user)
