from collections.abc import Iterator

from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)


def session_factory() -> Session:
    return Session(engine)


def session_scope() -> Iterator[Session]:
    """Generator suitable for FastAPI Depends."""
    s = session_factory()
    try:
        yield s
    finally:
        s.close()
