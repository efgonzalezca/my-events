from typing import Protocol

from app.modules.sessions.domain.entities import Session


class SessionRepository(Protocol):
    def add(self, session: Session) -> Session: ...

    def list_by_event(self, event_id: int) -> list[Session]:
        """Return all sessions of the given event, ordered by start asc."""
        ...

    def get(self, session_id: int) -> Session:
        """Return the session by id; raise SessionNotFound if it does not exist."""
        ...

    def update(self, session: Session) -> Session:
        """Persist mutable fields; raise SessionNotFound if missing."""
        ...

    def delete(self, session_id: int) -> None:
        """Remove the session by id; raise SessionNotFound if it does not exist."""
        ...

    def link_speaker(self, session_id: int, speaker_id: int) -> None:
        """Add a (session, speaker) link; raise SessionNotFound or SpeakerAlreadyLinked."""
        ...

    def unlink_speaker(self, session_id: int, speaker_id: int) -> None:
        """Remove a (session, speaker) link; raise SessionNotFound or SpeakerNotLinked."""
        ...

    def list_speaker_ids(self, session_id: int) -> list[int]:
        """Return the ids of speakers linked to the session."""
        ...