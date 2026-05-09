from app.modules.identity.domain.entities import User
from app.modules.identity.domain.value_objects import Email
from app.modules.identity.infrastructure.orm import UserORM


def to_domain(orm: UserORM) -> User:
    assert orm.id is not None
    return User(
        id=orm.id,
        email=Email(orm.email),
        full_name=orm.full_name,
        password_hash=orm.password_hash,
        role=orm.role,
        is_active=orm.is_active,
        created_at=orm.created_at,
    )


def to_orm(user: User) -> UserORM:
    return UserORM(
        id=user.id,
        email=user.email.value,
        full_name=user.full_name,
        password_hash=user.password_hash,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )
