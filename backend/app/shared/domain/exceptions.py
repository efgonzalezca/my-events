class DomainError(Exception):
    """Base for all domain errors. interfaces/http maps to HTTP status."""

    code: str = "DOMAIN_ERROR"
