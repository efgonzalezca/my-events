from app.shared.domain.exceptions import DomainError


class SpeakerNotFound(DomainError):
    code = "SPEAKER_NOT_FOUND"
