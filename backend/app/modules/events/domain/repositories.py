from typing import Protocol

from app.modules.events.domain.entities import Event


class EventRepository(Protocol):
    def add(self, event: Event) -> Event: ...
