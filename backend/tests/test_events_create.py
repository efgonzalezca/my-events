from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.modules.identity.domain.entities import UserRole
from tests.conftest import promote_user


def _register_and_login(
    client: TestClient,
    email: str,
    full_name: str,
    password: str = "S1$#a1pa$$w0rd",
) -> str:
    client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    res = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    return res.json()["access_token"]


def _payload() -> dict:
    starts = datetime.now(timezone.utc) + timedelta(days=1)
    ends = starts + timedelta(hours=2)
    return {
        "name": "PyConf",
        "description": "Annual python conference",
        "location": "Bogota",
        "starts_at": starts.isoformat(),
        "ends_at": ends.isoformat(),
        "capacity": 100,
    }


def test_create_event_as_organizer_returns_201(
    client: TestClient, engine
) -> None:
    token = _register_and_login(client, "org@test.com", "Org One")
    promote_user(engine, "org@test.com", UserRole.organizer)

    res = client.post(
        "/api/events",
        json=_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 201, res.text
    body = res.json()
    assert body["status"] == "draft"
    assert body["registered_count"] == 0
    assert isinstance(body["id"], int)
    assert body["organizer_id"] >= 1


def test_create_event_as_admin_returns_201(client: TestClient, engine) -> None:
    token = _register_and_login(client, "admin@test.com", "Admin")
    promote_user(engine, "admin@test.com", UserRole.admin)

    res = client.post(
        "/api/events",
        json=_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 201, res.text


def test_create_event_as_attendee_is_forbidden(client: TestClient) -> None:
    token = _register_and_login(client, "att@test.com", "Att")
    res = client.post(
        "/api/events",
        json=_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403


def test_create_event_without_token_is_rejected(client: TestClient) -> None:
    res = client.post("/api/events", json=_payload())
    assert res.status_code in (401, 403)
