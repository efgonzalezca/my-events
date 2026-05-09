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


def _seed_published_event(engine, capacity: int = 10) -> int:
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
                status=EventStatus.published,
            )
        )
        return added.id


def test_register_then_cancel_returns_204(
    client: TestClient, engine
) -> None:
    token = _register_login(client, "att@test.com")
    event_id = _seed_published_event(engine)

    client.post(
        f"/api/events/{event_id}/register",
        headers={"Authorization": f"Bearer {token}"},
    )

    res = client.delete(
        f"/api/events/{event_id}/register",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 204, res.text
    assert res.content == b""

    detail = client.get(f"/api/events/{event_id}").json()
    assert detail["registered_count"] == 0