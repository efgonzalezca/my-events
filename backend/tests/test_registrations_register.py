from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.events.domain.entities import Event
from app.modules.events.domain.value_objects import DateRange, EventStatus
from app.modules.events.infrastructure.repositories import SqlEventRepository


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


def _seed_event(engine, status: EventStatus, capacity: int = 10) -> int:
    starts = datetime.now(timezone.utc) + timedelta(days=1)
    with Session(engine) as s:
        added = SqlEventRepository(s).add(
            Event(
                id=None,
                name="Evt",
                description="",
                location="",
                schedule=DateRange(starts, starts + timedelta(hours=2)),
                capacity=capacity,
                organizer_id=1,
                status=status,
            )
        )
        return added.id


def test_register_to_published_event_returns_201(
    client: TestClient, engine
) -> None:
    token = _register_login(client, "att@test.com")
    event_id = _seed_event(engine, EventStatus.published)

    res = client.post(
        f"/api/events/{event_id}/register",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 201, res.text
    body = res.json()
    assert body["event_id"] == event_id
    assert isinstance(body["id"], int)


def test_register_to_draft_event_returns_409_not_published(
    client: TestClient, engine
) -> None:
    token = _register_login(client, "att@test.com")
    event_id = _seed_event(engine, EventStatus.draft)

    res = client.post(
        f"/api/events/{event_id}/register",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 409, res.text
    assert res.json()["code"] == "NOT_PUBLISHED"