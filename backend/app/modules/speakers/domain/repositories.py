from typing import Protocol

from app.modules.speakers.domain.entities import Speaker


class SpeakerRepository(Protocol):
    def add(self, speaker: Speaker) -> Speaker: ...