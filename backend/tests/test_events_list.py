from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.events.domain.entities import Event
from app.modules.events.domain.value_objects import DateRange, EventStatus
from app.modules.events.infrastructure.repositories import SqlEventRepository
from app.modules.identity.domain.entities import UserRole
from app.modules.identity.infrastructure.orm import UserORM
from app.shared.infrastructure.security.bcrypt_hasher import BcryptHasher


def _seed_organizer(engine) -> int:
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
        return user.id


def _seed_event(
    engine,
    organizer_id: int,
    name: str,
    status: EventStatus,
    starts_at: datetime,
) -> int:
    with Session(engine) as s:
        repo = SqlEventRepository(s)
        event = Event(
            id=None,
            name=name,
            description="",
            location="",
            schedule=DateRange(starts_at, starts_at + timedelta(hours=1)),
            capacity=10,
            organizer_id=organizer_id,
            status=status,
        )
        added = repo.add(event)
        return added.id


def test_list_empty_returns_zero_total(client: TestClient) -> None:
    res = client.get("/api/events")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body == {"items": [], "page": 1, "size": 20, "total": 0}


def test_list_only_returns_published_events(client: TestClient, engine) -> None:
    org_id = _seed_organizer(engine)
    base = datetime.now(timezone.utc) + timedelta(days=1)
    _seed_event(engine, org_id, "DraftOne", EventStatus.draft, base)
    _seed_event(
        engine, org_id, "PubOne", EventStatus.published, base + timedelta(hours=2)
    )

    res = client.get("/api/events")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "PubOne"
    assert body["items"][0]["status"] == "published"


def test_list_q_filters_by_name_case_insensitive(
    client: TestClient, engine
) -> None:
    org_id = _seed_organizer(engine)
    base = datetime.now(timezone.utc) + timedelta(days=1)
    _seed_event(engine, org_id, "PyConf", EventStatus.published, base)
    _seed_event(
        engine,
        org_id,
        "JsConf",
        EventStatus.published,
        base + timedelta(hours=2),
    )

    res = client.get("/api/events", params={"q": "pyc"})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "PyConf"


def test_list_pagination_returns_correct_pages_and_total(
    client: TestClient, engine
) -> None:
    org_id = _seed_organizer(engine)
    base = datetime.now(timezone.utc) + timedelta(days=1)
    for i in range(3):
        _seed_event(
            engine,
            org_id,
            f"Evt{i}",
            EventStatus.published,
            base + timedelta(hours=i),
        )

    page1 = client.get("/api/events", params={"page": 1, "size": 2}).json()
    page2 = client.get("/api/events", params={"page": 2, "size": 2}).json()

    assert page1["total"] == 3
    assert page2["total"] == 3
    assert len(page1["items"]) == 2
    assert len(page2["items"]) == 1
    assert page1["page"] == 1
    assert page2["page"] == 2
    ids_p1 = {e["id"] for e in page1["items"]}
    ids_p2 = {e["id"] for e in page2["items"]}
    assert ids_p1.isdisjoint(ids_p2)