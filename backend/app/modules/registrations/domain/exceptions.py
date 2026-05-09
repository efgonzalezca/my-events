from app.shared.domain.exceptions import DomainError


class RegistrationNotFound(DomainError):
    code = "REGISTRATION_NOT_FOUND"


class AlreadyRegistered(DomainError):
    code = "ALREADY_REGISTERED"


class EventFull(DomainError):
    code = "EVENT_FULL"


class NotPublished(DomainError):
    code = "NOT_PUBLISHED"