import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.main import app
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