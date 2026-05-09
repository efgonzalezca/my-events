from app.shared.domain.exceptions import DomainError


class EventNotFound(DomainError):
    code = "EVENT_NOT_FOUND"


class InvalidStatusTransition(DomainError):
    code = "INVALID_STATUS_TRANSITION"


class EventNotModifiable(DomainError):
    code = "EVENT_NOT_MODIFIABLE"


class EventNotOwned(DomainError):
    code = "EVENT_NOT_OWNED"


class CapacityBelowRegistered(DomainError):
    code = "CAPACITY_BELOW_REGISTERED"
