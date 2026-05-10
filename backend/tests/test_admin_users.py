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


def test_admin_lists_users_returns_200_with_total(
    client: TestClient, engine
) -> None:
    admin_token = _register_login(client, "admin@test.com")
    promote_user(engine, "admin@test.com", UserRole.admin)
    _register_login(client, "att@test.com")

    res = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total"] == 2
    emails = {item["email"] for item in body["items"]}
    assert emails == {"admin@test.com", "att@test.com"}


def test_attendee_listing_users_is_forbidden(client: TestClient) -> None:
    token = _register_login(client, "att@test.com")

    res = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 403