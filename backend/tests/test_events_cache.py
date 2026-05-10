from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.events.domain.entities import Event
from app.modules.events.domain.value_objects import DateRange, EventStatus
from app.modules.events.infrastructure.repositories import SqlEventRepository
from app.modules.identity.domain.entities import UserRole
from app.modules.identity.infrastructure.orm import UserORM
from app.shared.infrastructure.security.bcrypt_hasher import BcryptHasher
from tests.fakes import FakeCache


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


def _promote(engine, email: str, role: UserRole) -> None:
    from sqlmodel import select
    with Session(engine) as s:
        user = s.exec(select(UserORM).where(UserORM.email == email)).one()
        user.role = role
        s.add(user)
        s.commit()


def _seed_published_event(engine, organizer_id: int) -> int:
    with Session(engine) as s:
        repo = SqlEventRepository(s)
        starts = datetime.now(timezone.utc) + timedelta(days=1)
        event = Event(
            id=None,
            name="Cached",
            description="",
            location="",
            schedule=DateRange(starts, starts + timedelta(hours=1)),
            capacity=10,
            organizer_id=organizer_id,
            status=EventStatus.published,
        )
        return repo.add(event).id


def test_list_published_caches_response_then_invalidates_on_create(
    client: TestClient, engine, fake_cache: FakeCache
) -> None:
    with Session(engine) as s:
        user = UserORM(
            email="seed@test.com",
            full_name="Seed",
            password_hash=BcryptHasher().hash("S1$#a1pa$$w0rd"),
            role=UserRole.organizer,
        )
        s.add(user)
        s.commit()
        s.refresh(user)
        org_id = user.id
    _seed_published_event(engine, org_id)

    first = client.get("/api/events")
    assert first.status_code == 200, first.text
    assert first.json()["total"] == 1
    assert len([k for k in fake_cache.store if k.startswith("events:list:")]) == 1

    second = client.get("/api/events")
    assert second.status_code == 200
    assert second.json() == first.json()

    org_token = _register_login(client, "org@test.com")
    _promote(engine, "org@test.com", UserRole.organizer)
    starts = datetime.now(timezone.utc) + timedelta(days=2)
    create = client.post(
        "/api/events",
        headers={"Authorization": f"Bearer {org_token}"},
        json={
            "name": "New",
            "description": "",
            "location": "",
            "starts_at": starts.isoformat(),
            "ends_at": (starts + timedelta(hours=1)).isoformat(),
            "capacity": 10,
        },
    )
    assert create.status_code == 201, create.text
    assert not any(k.startswith("events:") for k in fake_cache.store)