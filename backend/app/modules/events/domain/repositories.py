from typing import Protocol

from app.modules.events.domain.entities import Event


class EventRepository(Protocol):
    def add(self, event: Event) -> Event: ...

    def list_published(
        self, q: str | None, offset: int, limit: int
    ) -> tuple[list[Event], int]:
        """Return (items, total) for events with status == published.

        If q is provided, filters by name case-insensitive (ILIKE %q%).
        Total is the count after filtering, before paginating.
        """
        ...

    def get(self, event_id: int) -> Event:
        """Return the event by id; raise EventNotFound if it does not exist."""
        ...

    def update(self, event: Event) -> Event:
        """Persist mutable fields of the given event; raise EventNotFound if missing."""
        ...