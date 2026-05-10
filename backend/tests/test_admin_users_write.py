from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.modules.identity.domain.entities import UserRole
from app.modules.identity.infrastructure.orm import UserORM
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


def _user_id(engine, email: str) -> int:
    with Session(engine) as s:
        return s.exec(select(UserORM).where(UserORM.email == email)).one().id


def test_admin_changes_other_user_role_returns_200(
    client: TestClient, engine
) -> None:
    admin_token = _register_login(client, "admin@test.com")
    promote_user(engine, "admin@test.com", UserRole.admin)
    _register_login(client, "att@test.com")
    target_id = _user_id(engine, "att@test.com")

    res = client.patch(
        f"/api/admin/users/{target_id}/role",
        json={"role": "organizer"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert res.status_code == 200, res.text
    assert res.json()["role"] == "organizer"


def test_admin_modifying_self_returns_409_cannot_modify_self(
    client: TestClient, engine
) -> None:
    admin_token = _register_login(client, "admin@test.com")
    promote_user(engine, "admin@test.com", UserRole.admin)
    admin_id = _user_id(engine, "admin@test.com")

    res = client.patch(
        f"/api/admin/users/{admin_id}/role",
        json={"role": "attendee"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert res.status_code == 409, res.text
    assert res.json()["code"] == "CANNOT_MODIFY_SELF"