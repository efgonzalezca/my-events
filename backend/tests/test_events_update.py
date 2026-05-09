from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.modules.events.domain.entities import Event
from app.modules.events.domain.value_objects import DateRange, EventStatus
from app.modules.events.infrastructure.orm import EventORM
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
    name: str = "Evt",
    status: EventStatus = EventStatus.draft,
) -> int:
    starts = datetime.now(timezone.utc) + timedelta(days=1)
    with Session(engine) as s:
        repo = SqlEventRepository(s)
        added = repo.add(
            Event(
                id=None,
                name=name,
                description="",
                location="",
                schedule=DateRange(starts, starts + timedelta(hours=2)),
                capacity=10,
                organizer_id=organizer_id,
                status=status,
            )
        )
        return added.id


def _set_registered_count(engine, event_id: int, count: int) -> None:
    with Session(engine) as s:
        orm = s.get(EventORM, event_id)
        orm.registered_count = count
        s.add(orm)
        s.commit()


def test_organizer_owner_updates_own_draft_returns_200(
    client: TestClient, engine
) -> None:
    token, uid = _register_login_promote(
        client, engine, "owner@test.com", UserRole.organizer
    )
    event_id = _seed_event(engine, uid, name="Old")

    res = client.patch(
        f"/api/events/{event_id}",
        json={"name": "New", "capacity": 50},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["name"] == "New"
    assert body["capacity"] == 50


def test_admin_updates_others_event_returns_200(
    client: TestClient, engine
) -> None:
    _, owner_id = _register_login_promote(
        client, engine, "owner@test.com", UserRole.organizer
    )
    event_id = _seed_event(engine, owner_id)
    admin_token, _ = _register_login_promote(
        client, engine, "admin@test.com", UserRole.admin
    )

    res = client.patch(
        f"/api/events/{event_id}",
        json={"name": "AdminTouched"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["name"] == "AdminTouched"


def test_organizer_not_owner_is_forbidden(
    client: TestClient, engine
) -> None:
    _, owner_id = _register_login_promote(
        client, engine, "owner@test.com", UserRole.organizer
    )
    event_id = _seed_event(engine, owner_id)
    other_token, _ = _register_login_promote(
        client, engine, "other@test.com", UserRole.organizer
    )

    res = client.patch(
        f"/api/events/{event_id}",
        json={"name": "X"},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert res.status_code == 403, res.text
    assert res.json()["code"] == "EVENT_NOT_OWNED"


def test_patch_published_event_returns_409_not_modifiable(
    client: TestClient, engine
) -> None:
    token, uid = _register_login_promote(
        client, engine, "owner@test.com", UserRole.organizer
    )
    event_id = _seed_event(engine, uid, status=EventStatus.published)

    res = client.patch(
        f"/api/events/{event_id}",
        json={"name": "X"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 409, res.text
    assert res.json()["code"] == "EVENT_NOT_MODIFIABLE"


def test_patch_capacity_below_registered_returns_409(
    client: TestClient, engine
) -> None:
    token, uid = _register_login_promote(
        client, engine, "owner@test.com", UserRole.organizer
    )
    event_id = _seed_event(engine, uid)
    _set_registered_count(engine, event_id, 5)

    res = client.patch(
        f"/api/events/{event_id}",
        json={"capacity": 2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 409, res.text
    assert res.json()["code"] == "CAPACITY_BELOW_REGISTERED"


def test_patch_nonexistent_event_returns_404(
    client: TestClient, engine
) -> None:
    token, _ = _register_login_promote(
        client, engine, "owner@test.com", UserRole.organizer
    )
    res = client.patch(
        "/api/events/9999",
        json={"name": "X"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 404, res.text
    assert res.json()["code"] == "EVENT_NOT_FOUND"