from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.events.domain.entities import Event
from app.modules.events.domain.value_objects import DateRange, EventStatus
from app.modules.events.infrastructure.repositories import SqlEventRepository
from app.modules.identity.domain.entities import UserRole
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


def _seed_event(engine, organizer_id: int = 1) -> tuple[int, datetime, datetime]:
    starts = datetime.now(timezone.utc) + timedelta(days=1)
    ends = starts + timedelta(hours=4)
    with Session(engine) as s:
        repo = SqlEventRepository(s)
        added = repo.add(
            Event(
                id=None,
                name="Evt",
                description="",
                location="",
                schedule=DateRange(starts, ends),
                capacity=100,
                organizer_id=organizer_id,
                status=EventStatus.draft,
            )
        )
        return added.id, starts, ends


def test_organizer_creates_session_inside_event_range_returns_201(
    client: TestClient, engine
) -> None:
    token = _register_login(client, "org@test.com")
    promote_user(engine, "org@test.com", UserRole.organizer)
    event_id, starts, ends = _seed_event(engine)

    res = client.post(
        f"/api/events/{event_id}/sessions",
        json={
            "title": "Keynote",
            "description": "Opening",
            "starts_at": (starts + timedelta(minutes=30)).isoformat(),
            "ends_at": (starts + timedelta(hours=1, minutes=30)).isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 201, res.text
    body = res.json()
    assert body["event_id"] == event_id
    assert body["title"] == "Keynote"
    assert body["speaker_ids"] == []


def test_create_session_outside_event_range_returns_409(
    client: TestClient, engine
) -> None:
    token = _register_login(client, "org@test.com")
    promote_user(engine, "org@test.com", UserRole.organizer)
    event_id, _, ends = _seed_event(engine)

    res = client.post(
        f"/api/events/{event_id}/sessions",
        json={
            "title": "After-party",
            "description": "",
            "starts_at": (ends + timedelta(hours=1)).isoformat(),
            "ends_at": (ends + timedelta(hours=2)).isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 409, res.text
    assert res.json()["code"] == "SESSION_OUT_OF_EVENT_RANGE"