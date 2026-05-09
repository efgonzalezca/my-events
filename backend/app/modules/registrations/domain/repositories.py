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