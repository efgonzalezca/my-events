from typing import Protocol

from app.modules.speakers.domain.entities import Speaker


class SpeakerRepository(Protocol):
    def add(self, speaker: Speaker) -> Speaker: ...

    def get(self, speaker_id: int) -> Speaker:
        """Return the speaker by id; raise SpeakerNotFound if it does not exist."""
        ...

    def list_all(
        self, q: str | None, offset: int, limit: int
    ) -> tuple[list[Speaker], int]:
        """Return (items, total). If q is provided, filters by name case-insensitive."""
        ...