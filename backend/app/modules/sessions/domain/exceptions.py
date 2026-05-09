from app.shared.domain.exceptions import DomainError


class SessionNotFound(DomainError):
    code = "SESSION_NOT_FOUND"


class SessionOutOfEventRange(DomainError):
    code = "SESSION_OUT_OF_EVENT_RANGE"


class SessionScheduleConflict(DomainError):
    code = "SESSION_SCHEDULE_CONFLICT"