"""Populate the database with demo data for the frontend.

Run after `make clean-db` (or against an empty DB). All users share the same
password to ease manual testing.

    docker compose ... exec backend python scripts/seed.py

Or via Makefile:

    make seed
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.modules.events.domain.entities import Event
from app.modules.events.domain.value_objects import DateRange, EventStatus
from app.modules.events.infrastructure.repositories import SqlEventRepository
from app.modules.identity.domain.entities import User, UserRole
from app.modules.identity.domain.value_objects import Email
from app.modules.identity.infrastructure.orm import UserORM
from app.modules.identity.infrastructure.repositories import SqlUserRepository
from app.modules.registrations.infrastructure.repositories import (
    SqlRegistrationRepository,
)
from app.modules.sessions.domain.entities import Session as DomainSession
from app.modules.sessions.infrastructure.repositories import SqlSessionRepository
from app.modules.speakers.domain.entities import Speaker
from app.modules.speakers.infrastructure.repositories import SqlSpeakerRepository
from app.shared.infrastructure.db import session_factory
from app.shared.infrastructure.security.bcrypt_hasher import BcryptHasher


PASSWORD = "Test1234$"


def _ensure_empty(s: Session) -> None:
    existing = s.exec(select(UserORM).limit(1)).first()
    if existing is not None:
        raise SystemExit(
            "Database is not empty. Run `make clean-db` first to wipe it."
        )


def _create_users(s: Session) -> dict[str, int]:
    repo = SqlUserRepository(s)
    hasher = BcryptHasher()
    pw_hash = hasher.hash(PASSWORD)

    specs: list[tuple[str, str, UserRole]] = [
        ("admin@miseventos.com", "Admin Root", UserRole.admin),
        ("org1@miseventos.com", "Camila Ortiz", UserRole.organizer),
        ("org2@miseventos.com", "Daniel Suarez", UserRole.organizer),
        ("org3@miseventos.com", "Mariana Lopez", UserRole.organizer),
        ("org4@miseventos.com", "Andres Pinto", UserRole.organizer),
        ("att1@miseventos.com", "Alice Reyes", UserRole.attendee),
        ("att2@miseventos.com", "Bruno Castro", UserRole.attendee),
        ("att3@miseventos.com", "Carla Mendez", UserRole.attendee),
        ("att4@miseventos.com", "Diego Tovar", UserRole.attendee),
        ("att5@miseventos.com", "Elena Rojas", UserRole.attendee),
        ("att6@miseventos.com", "Felipe Niño", UserRole.attendee),
        ("att7@miseventos.com", "Gabriela Soto", UserRole.attendee),
        ("att8@miseventos.com", "Hector Vargas", UserRole.attendee),
    ]

    ids: dict[str, int] = {}
    for email, name, role in specs:
        added = repo.add(
            User(
                id=None,
                email=Email(email),
                full_name=name,
                password_hash=pw_hash,
                role=role,
            )
        )
        ids[email] = added.id
    return ids


def _create_speakers(s: Session) -> list[int]:
    repo = SqlSpeakerRepository(s)
    specs = [
        ("Ada Lovelace", "Pioneer of computing."),
        ("Grace Hopper", "Compiler innovator."),
        ("Linus Torvalds", "Creator of Linux."),
        ("Guido van Rossum", "Python's BDFL."),
        ("Brendan Eich", "Created JavaScript."),
        ("Margaret Hamilton", "Apollo flight software."),
    ]
    return [
        repo.add(Speaker(id=None, name=n, bio=b, photo_url="")).id
        for (n, b) in specs
    ]


def _create_events(s: Session, organizer_ids: list[int]) -> list[int]:
    """Return event ids in declaration order."""
    repo = SqlEventRepository(s)
    now = datetime.now(timezone.utc)

    # (offset_days, name, location, capacity, status, organizer_idx)
    specs = [
        # PAST (4) — all published
        (-60, "Tech Summit 2026 Q1", "Bogota", 200, EventStatus.published, 0),
        (-30, "Mobile Devs Meetup", "Medellin", 80, EventStatus.published, 1),
        (-14, "AI Hackathon", "Cali", 100, EventStatus.published, 2),
        (-7, "Startup Pitch Night", "Bogota", 50, EventStatus.published, 3),
        # FUTURE published (5)
        (7, "PyConf Bogota 2026", "Bogota", 250, EventStatus.published, 0),
        (14, "DevOps Day Latam", "Medellin", 150, EventStatus.published, 1),
        (21, "JS Nation", "Bogota", 200, EventStatus.published, 2),
        (30, "Data Engineering Summit", "Cartagena", 100, EventStatus.published, 3),
        (45, "Cybersecurity Conf", "Bogota", 120, EventStatus.published, 0),
        # FUTURE non-published (4)
        (60, "Cloud Native Day", "Medellin", 180, EventStatus.draft, 1),
        (75, "Frontend Masters Live", "Bogota", 80, EventStatus.draft, 2),
        (90, "Game Dev Workshop", "Cali", 60, EventStatus.cancelled, 3),
        (100, "Open Source Summit", "Bogota", 140, EventStatus.draft, 0),
    ]

    ids = []
    for offset_days, name, location, capacity, status, org_idx in specs:
        starts = now + timedelta(days=offset_days, hours=9)  # 9am day-of
        ends = starts + timedelta(hours=8)  # 8h event window
        added = repo.add(
            Event(
                id=None,
                name=name,
                description=f"Demo event: {name}.",
                location=location,
                schedule=DateRange(starts, ends),
                capacity=capacity,
                organizer_id=organizer_ids[org_idx],
                status=status,
            )
        )
        ids.append(added.id)
    return ids


def _create_sessions(
    s: Session, event_ids: list[int], event_starts: list[datetime]
) -> list[int]:
    """Two sessions per past published, three per future published. Skip drafts/cancelled."""
    repo = SqlSessionRepository(s)
    sessions_per_event = [2, 2, 2, 2, 3, 3, 3, 3, 3, 0, 0, 0, 0]

    titles = [
        "Opening Keynote",
        "Technical Deep Dive",
        "Panel Discussion",
        "Hands-on Workshop",
    ]

    session_ids: list[int] = []
    for evt_idx, n_sessions in enumerate(sessions_per_event):
        event_start = event_starts[evt_idx]
        for i in range(n_sessions):
            # Each session 1.5h, spaced 2h apart starting 0:00 from event start
            s_start = event_start + timedelta(hours=i * 2)
            s_end = s_start + timedelta(hours=1, minutes=30)
            added = repo.add(
                DomainSession(
                    id=None,
                    event_id=event_ids[evt_idx],
                    title=titles[i],
                    description=f"Session {i + 1}: {titles[i]}.",
                    schedule=DateRange(s_start, s_end),
                )
            )
            session_ids.append(added.id)
    return session_ids


def _link_speakers(
    s: Session, session_ids: list[int], speaker_ids: list[int]
) -> int:
    """One speaker per session, rotating through the speaker pool."""
    repo = SqlSessionRepository(s)
    n = 0
    for i, sess_id in enumerate(session_ids):
        repo.link_speaker(sess_id, speaker_ids[i % len(speaker_ids)])
        n += 1
    return n


def _register_attendees(
    s: Session, attendee_ids: list[int], event_ids: list[int]
) -> int:
    """Distribute registrations across the 9 published events (idx 0..8)."""
    repo = SqlRegistrationRepository(s)
    # Pre-built attendee → list of published-event indices (0..8)
    plan: list[list[int]] = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [0, 1, 2, 4, 5, 7],
        [0, 1, 3, 4, 7],
        [0, 2, 4, 5, 7],
        [1, 2, 5, 8],
        [0, 3, 4, 6],
        [4, 5, 7],
        [4, 8],
    ]
    n = 0
    for att_idx, evt_indices in enumerate(plan):
        for evt_idx in evt_indices:
            repo.try_register(attendee_ids[att_idx], event_ids[evt_idx])
            n += 1
    return n


def seed() -> None:
    with session_factory() as s:
        _ensure_empty(s)

        user_ids = _create_users(s)
        speaker_ids = _create_speakers(s)

        organizer_ids = [
            user_ids["org1@miseventos.com"],
            user_ids["org2@miseventos.com"],
            user_ids["org3@miseventos.com"],
            user_ids["org4@miseventos.com"],
        ]
        attendee_ids = [user_ids[f"att{i}@miseventos.com"] for i in range(1, 9)]

        event_ids = _create_events(s, organizer_ids)

        # Recover the event start datetimes for session scheduling.
        now = datetime.now(timezone.utc)
        offsets = [-60, -30, -14, -7, 7, 14, 21, 30, 45, 60, 75, 90, 100]
        event_starts = [
            now + timedelta(days=d, hours=9) for d in offsets
        ]

        session_ids = _create_sessions(s, event_ids, event_starts)
        n_links = _link_speakers(s, session_ids, speaker_ids)
        n_regs = _register_attendees(s, attendee_ids, event_ids)

    print("Seed complete.")
    print(f"  users:         {len(user_ids)}  (password: {PASSWORD})")
    print(f"  speakers:      {len(speaker_ids)}")
    print(f"  events:        {len(event_ids)}  (4 past + 9 future)")
    print(f"  sessions:      {len(session_ids)}")
    print(f"  speaker links: {n_links}")
    print(f"  registrations: {n_regs}")
    print()
    print("Demo logins:")
    print("  admin@miseventos.com    (admin)")
    print("  org1..org4@miseventos.com (organizer)")
    print("  att1..att8@miseventos.com (attendee)")


if __name__ == "__main__":
    seed()