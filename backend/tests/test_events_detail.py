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
    engine, organizer_id: int, name: str, status: EventStatus
) -> int:
    starts = datetime.now(timezone.utc) + timedelta(days=1)
    with Session(engine) as s:
        repo = SqlEventRepository(s)
        added = repo.add(
            Event(
                id=None,
                name=name,
                description="An event",
                location="Bogota",
                schedule=DateRange(starts, starts + timedelta(hours=2)),
                capacity=100,
                organizer_id=organizer_id,
                status=status,
            )
        )
        return added.id


def test_get_event_returns_full_body_for_draft_and_published(
    client: TestClient, engine
) -> None:
    org_id = _seed_organizer(engine)
    draft_id = _seed_event(engine, org_id, "DraftEvt", EventStatus.draft)
    pub_id = _seed_event(engine, org_id, "PubEvt", EventStatus.published)

    for evt_id, name, status in (
        (draft_id, "DraftEvt", "draft"),
        (pub_id, "PubEvt", "published"),
    ):
        res = client.get(f"/api/events/{evt_id}")
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["id"] == evt_id
        assert body["name"] == name
        assert body["status"] == status
        assert body["organizer_id"] == org_id
        assert body["capacity"] == 100
        assert body["registered_count"] == 0


def test_get_event_returns_404_with_code_when_not_found(
    client: TestClient,
) -> None:
    res = client.get("/api/events/9999")
    assert res.status_code == 404, res.text
    assert res.json()["code"] == "EVENT_NOT_FOUND"