from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.identity.domain.entities import UserRole
from app.modules.speakers.domain.entities import Speaker
from app.modules.speakers.infrastructure.repositories import SqlSpeakerRepository
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


def _seed_speaker(engine, name: str = "Ada Lovelace") -> int:
    with Session(engine) as s:
        repo = SqlSpeakerRepository(s)
        added = repo.add(
            Speaker(id=None, name=name, bio="old bio", photo_url="")
        )
        return added.id


def test_organizer_patches_speaker_returns_200_with_updated_fields(
    client: TestClient, engine
) -> None:
    token = _register_login(client, "org@test.com")
    promote_user(engine, "org@test.com", UserRole.organizer)
    speaker_id = _seed_speaker(engine)

    res = client.patch(
        f"/api/speakers/{speaker_id}",
        json={"name": "Ada L.", "bio": "updated"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 200, res.text
    body = res.json()
    assert body["name"] == "Ada L."
    assert body["bio"] == "updated"


def test_attendee_delete_speaker_is_forbidden(
    client: TestClient, engine
) -> None:
    token = _register_login(client, "att@test.com")
    speaker_id = _seed_speaker(engine)

    res = client.delete(
        f"/api/speakers/{speaker_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 403