from typing import Protocol

from app.modules.registrations.domain.entities import Registration


class RegistrationRepository(Protocol):
    def try_register(self, user_id: int, event_id: int) -> Registration:
        """Atomic capacity-checked registration.

        Increments events.registered_count only if the event is published and
        has spare capacity, then inserts a row in registrations with UNIQUE
        (user_id, event_id). On conflict the whole transaction is rolled back.

        Raises EventNotFound, NotPublished, EventFull or AlreadyRegistered.
        """
        ...

    def cancel(self, user_id: int, event_id: int) -> None:
        """Remove the user's registration and decrement events.registered_count
        guarded against negatives. Raises RegistrationNotFound if missing."""
        ...

    def list_by_user(self, user_id: int) -> list[Registration]:
        """Return all registrations of the user, newest first."""
        ...