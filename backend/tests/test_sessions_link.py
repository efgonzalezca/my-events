from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.events.domain.entities import Event
from app.modules.events.domain.value_objects import DateRange, EventStatus
from app.modules.events.infrastructure.repositories import SqlEventRepository
from app.modules.identity.domain.entities import UserRole
from app.modules.sessions.domain.entities import Session as DomainSession
from app.modules.sessions.infrastructure.repositories import (
    SqlSessionRepository,
)
from app.modules.speakers.domain.entities import Speaker
from app.modules.speakers.infrastructure.repositories import (
    SqlSpeakerRepository,
)
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


def _seed_session_and_speaker(engine) -> tuple[int, int]:
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
        sp = SqlSpeakerRepository(s).add(
            Speaker(id=None, name="Ada", bio="", photo_url="")
        )
        return sess.id, sp.id


def test_link_existing_speaker_returns_200_with_speaker_in_list(
    client: TestClient, engine
) -> None:
    token = _register_login(client, "org@test.com")
    promote_user(engine, "org@test.com", UserRole.organizer)
    session_id, speaker_id = _seed_session_and_speaker(engine)

    res = client.post(
        f"/api/sessions/{session_id}/speakers/{speaker_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 200, res.text
    body = res.json()
    assert speaker_id in body["speaker_ids"]


def test_link_missing_speaker_returns_404(client: TestClient, engine) -> None:
    token = _register_login(client, "org@test.com")
    promote_user(engine, "org@test.com", UserRole.organizer)
    session_id, _ = _seed_session_and_speaker(engine)

    res = client.post(
        f"/api/sessions/{session_id}/speakers/9999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 404, res.text
    assert res.json()["code"] == "SPEAKER_NOT_FOUND"