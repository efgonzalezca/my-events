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


def _seed_published_event(engine, name: str = "Evt") -> int:
    starts = datetime.now(timezone.utc) + timedelta(days=1)
    with Session(engine) as s:
        added = SqlEventRepository(s).add(
            Event(
                id=None,
                name=name,
                description="",
                location="Bogota",
                schedule=DateRange(starts, starts + timedelta(hours=2)),
                capacity=10,
                organizer_id=1,
                status=EventStatus.published,
            )
        )
        return added.id


def test_list_my_registrations_returns_event_summary(
    client: TestClient, engine
) -> None:
    token = _register_login(client, "att@test.com")
    event_id = _seed_published_event(engine, name="PyConf")

    client.post(
        f"/api/events/{event_id}/register",
        headers={"Authorization": f"Bearer {token}"},
    )

    res = client.get(
        "/api/me/registrations",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 200, res.text
    body = res.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["event"]["id"] == event_id
    assert body[0]["event"]["name"] == "PyConf"
    assert body[0]["event"]["status"] == "published"