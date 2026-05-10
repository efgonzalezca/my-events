"""Truncate every domain table and restart identity sequences.

Targets Postgres. The alembic_version table is preserved so the migration
history stays intact. Run inside the backend container:

    docker compose ... exec backend python scripts/clean.py

Or via Makefile:

    make clean-db
"""

from sqlalchemy import text

from app.shared.infrastructure.db import session_factory


# Single TRUNCATE with CASCADE so FK ordering does not matter and identity
# sequences reset to 1.
TRUNCATE_SQL = (
    'TRUNCATE TABLE '
    '"session_speaker_link", "registrations", "sessions", '
    '"events", "speakers", "users" '
    "RESTART IDENTITY CASCADE"
)


def clean() -> None:
    with session_factory() as s:
        s.execute(text(TRUNCATE_SQL))
        s.commit()
    print("Database cleaned (alembic_version preserved).")


if __name__ == "__main__":
    clean()