import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.main import app
from app.modules.identity.domain.entities import UserRole
from app.modules.identity.infrastructure.orm import UserORM
from app.shared.infrastructure.db import session_scope


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def client(engine) -> Iterator[TestClient]:
    def _override() -> Iterator[Session]:
        with Session(engine) as s:
            yield s

    app.dependency_overrides[session_scope] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def promote_user(engine, email: str, role: UserRole) -> None:
    """Update a user's role directly in the DB (admin module not yet wired)."""
    with Session(engine) as s:
        user = s.exec(select(UserORM).where(UserORM.email == email)).one()
        user.role = role
        s.add(user)
        s.commit()
