from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.events.domain.entities import Event
from app.modules.events.domain.value_objects import DateRange, EventStatus
from app.modules.events.infrastructure.repositories import SqlEventRepository
from app.modules.identity.domain.entities import UserRole
from app.modules.sessions.domain.entities import Session as DomainSession
from app.modules.sessions.infrastructure.repositories import (
    SqlSessionRepository,
)
from tests.conftest import promote_user


def _register_login(
    client: TestClient, email: str, password: str = "S1$#a1pa$$w0rd"
) -> str:
    client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": "X"},
    )
    return client.post(
        "/api/auth/login", json={"email": email, "password": password}
    ).json()["access_token"]


def _seed_event_with_session(engine) -> int:
    starts = datetime.now(timezone.utc) + timedelta(days=1)
    ends = starts + timedelta(hours=4)
    with Session(engine) as s:
        ev = SqlEventRepository(s).add(
            Event(
                id=None,
                name="Evt",
                description="",
                location="",
                schedule=DateRange(starts, ends),
                capacity=100,
                organizer_id=1,
                status=EventStatus.draft,
            )
        )
        sess = SqlSessionRepository(s).add(
            DomainSession(
                id=None,
                event_id=ev.id,
                title="Original",
                description="",
                schedule=DateRange(
                    starts + timedelta(hours=1),
                    starts + timedelta(hours=2),
                ),
            )
        )
        return sess.id


def test_organizer_patches_session_returns_200_with_updated_title(
    client: TestClient, engine
) -> None:
    token = _register_login(client, "org@test.com")
    promote_user(engine, "org@test.com", UserRole.organizer)
    session_id = _seed_event_with_session(engine)

    res = client.patch(
        f"/api/sessions/{session_id}",
        json={"title": "Updated"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 200, res.text
    assert res.json()["title"] == "Updated"


def test_organizer_deletes_session_then_get_returns_404(
    client: TestClient, engine
) -> None:
    token = _register_login(client, "org@test.com")
    promote_user(engine, "org@test.com", UserRole.organizer)
    session_id = _seed_event_with_session(engine)

    res = client.delete(
        f"/api/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 204, res.text
    assert res.content == b""

    after = client.get(f"/api/sessions/{session_id}")
    assert after.status_code == 404
    assert after.json()["code"] == "SESSION_NOT_FOUND"