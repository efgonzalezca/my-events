from sqlmodel import Session

from app.modules.speakers.application.ports import SpeakerExistsReader
from app.modules.speakers.infrastructure.orm import SpeakerORM


class SqlSpeakerExistsReader(SpeakerExistsReader):
    def __init__(self, session: Session) -> None:
        self._s = session

    def exists(self, speaker_id: int) -> bool:
        return self._s.get(SpeakerORM, speaker_id) is not None