from typing import Protocol


class SpeakerExistsReader(Protocol):
    def exists(self, speaker_id: int) -> bool:
        """Return True if a speaker with this id exists."""
        ...