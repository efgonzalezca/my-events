from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.events.domain.entities import Event
from app.modules.events.domain.value_objects import DateRange, EventStatus
from app.modules.events.infrastructure.repositories import SqlEventRepository
from app.modules.sessions.domain.entities import Session as DomainSession
from app.modules.sessions.infrastructure.repositories import (
    SqlSessionRepository,
)


def _seed_event_with_session(engine) -> tuple[int, int]:
    starts = datetime.now(timezone.utc) + timedelta(days=1)
    ends = starts + timedelta(hours=4)
    with Session(engine) as s:
        ev = SqlEventRepository(s).add(
            Event(
                id=None,
                name="Evt",
                description="",
                location="",
                schedule=DateRange(starts, ends),
                capacity=100,
                organizer_id=1,
                status=EventStatus.draft,
            )
        )
        sess = SqlSessionRepository(s).add(
            DomainSession(
                id=None,
                event_id=ev.id,
                title="Talk",
                description="",
                schedule=DateRange(
                    starts + timedelta(hours=1),
                    starts + timedelta(hours=2),
                ),
            )
        )
        return ev.id, sess.id


def test_list_sessions_of_event_returns_one_item(
    client: TestClient, engine
) -> None:
    event_id, session_id = _seed_event_with_session(engine)

    res = client.get(f"/api/events/{event_id}/sessions")
    assert res.status_code == 200, res.text
    body = res.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["id"] == session_id
    assert body[0]["event_id"] == event_id


def test_list_sessions_of_missing_event_returns_404(client: TestClient) -> None:
    res = client.get("/api/events/9999/sessions")
    assert res.status_code == 404, res.text
    assert res.json()["code"] == "EVENT_NOT_FOUND"