from fastapi.testclient import TestClient

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


def _payload() -> dict:
    return {
        "name": "Ada Lovelace",
        "bio": "Mathematician",
        "photo_url": "https://example.com/ada.png",
    }


def test_create_speaker_as_organizer_returns_201(
    client: TestClient, engine
) -> None:
    token = _register_login(client, "org@test.com")
    promote_user(engine, "org@test.com", UserRole.organizer)

    res = client.post(
        "/api/speakers",
        json=_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 201, res.text
    body = res.json()
    assert isinstance(body["id"], int)
    assert body["name"] == "Ada Lovelace"
    assert body["bio"] == "Mathematician"
    assert body["photo_url"] == "https://example.com/ada.png"


def test_create_speaker_as_attendee_is_forbidden(client: TestClient) -> None:
    token = _register_login(client, "att@test.com")

    res = client.post(
        "/api/speakers",
        json=_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 403