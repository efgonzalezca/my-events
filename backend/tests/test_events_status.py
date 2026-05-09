from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.modules.events.domain.entities import Event
from app.modules.events.domain.value_objects import DateRange, EventStatus
from app.modules.events.infrastructure.repositories import SqlEventRepository
from app.modules.identity.domain.entities import UserRole
from app.modules.identity.infrastructure.orm import UserORM
from tests.conftest import promote_user


def _register_login_promote(
    client: TestClient, engine, email: str, role: UserRole
) -> tuple[str, int]:
    password = "S1$#a1pa$$w0rd"
    client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": "X"},
    )
    promote_user(engine, email, role)
    token = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    ).json()["access_token"]
    with Session(engine) as s:
        uid = s.exec(select(UserORM).where(UserORM.email == email)).one().id
    return token, uid


def _seed_event(
    engine,
    organizer_id: int,
    status: EventStatus = EventStatus.draft,
) -> int:
    starts = datetime.now(timezone.utc) + timedelta(days=1)
    with Session(engine) as s:
        repo = SqlEventRepository(s)
        added = repo.add(
            Event(
                id=None,
                name="Evt",
                description="",
                location="",
                schedule=DateRange(starts, starts + timedelta(hours=2)),
                capacity=10,
                organizer_id=organizer_id,
                status=status,
            )
        )
        return added.id


def test_organizer_publishes_own_draft_returns_200(
    client: TestClient, engine
) -> None:
    token, uid = _register_login_promote(
        client, engine, "owner@test.com", UserRole.organizer
    )
    event_id = _seed_event(engine, uid, status=EventStatus.draft)

    res = client.post(
        f"/api/events/{event_id}/publish",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "published"


def test_admin_cancels_published_event_returns_200(
    client: TestClient, engine
) -> None:
    _, owner_id = _register_login_promote(
        client, engine, "owner@test.com", UserRole.organizer
    )
    event_id = _seed_event(engine, owner_id, status=EventStatus.published)
    admin_token, _ = _register_login_promote(
        client, engine, "admin@test.com", UserRole.admin
    )

    res = client.post(
        f"/api/events/{event_id}/cancel",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "cancelled"


def test_publish_already_published_returns_409_invalid_transition(
    client: TestClient, engine
) -> None:
    token, uid = _register_login_promote(
        client, engine, "owner@test.com", UserRole.organizer
    )
    event_id = _seed_event(engine, uid, status=EventStatus.published)

    res = client.post(
        f"/api/events/{event_id}/publish",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 409, res.text
    assert res.json()["code"] == "INVALID_STATUS_TRANSITION"


def test_publish_as_not_owner_is_forbidden(client: TestClient, engine) -> None:
    _, owner_id = _register_login_promote(
        client, engine, "owner@test.com", UserRole.organizer
    )
    event_id = _seed_event(engine, owner_id)
    other_token, _ = _register_login_promote(
        client, engine, "other@test.com", UserRole.organizer
    )

    res = client.post(
        f"/api/events/{event_id}/publish",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert res.status_code == 403, res.text
    assert res.json()["code"] == "EVENT_NOT_OWNED"