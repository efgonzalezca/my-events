from app.shared.domain.exceptions import DomainError


class EmailAlreadyExists(DomainError):
    code = "EMAIL_ALREADY_EXISTS"


class InvalidCredentials(DomainError):
    code = "INVALID_CREDENTIALS"


class UserNotFound(DomainError):
    code = "USER_NOT_FOUND"
