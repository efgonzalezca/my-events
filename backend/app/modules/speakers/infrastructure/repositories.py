from sqlalchemy import func
from sqlmodel import Session, select

from app.modules.speakers.domain.entities import Speaker
from app.modules.speakers.domain.exceptions import SpeakerNotFound
from app.modules.speakers.domain.repositories import SpeakerRepository
from app.modules.speakers.infrastructure.mappers import to_domain, to_orm
from app.modules.speakers.infrastructure.orm import SpeakerORM


class SqlSpeakerRepository(SpeakerRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, speaker: Speaker) -> Speaker:
        orm = to_orm(speaker)
        self._s.add(orm)
        self._s.commit()
        self._s.refresh(orm)
        return to_domain(orm)

    def get(self, speaker_id: int) -> Speaker:
        orm = self._s.get(SpeakerORM, speaker_id)
        if orm is None:
            raise SpeakerNotFound(str(speaker_id))
        return to_domain(orm)

    def list_all(
        self, q: str | None, offset: int, limit: int
    ) -> tuple[list[Speaker], int]:
        filters = []
        if q:
            filters.append(SpeakerORM.name.ilike(f"%{q}%"))

        items_stmt = (
            select(SpeakerORM)
            .where(*filters)
            .order_by(SpeakerORM.name.asc())
            .offset(offset)
            .limit(limit)
        )
        count_stmt = select(func.count()).select_from(SpeakerORM).where(*filters)

        rows = self._s.exec(items_stmt).all()
        total = self._s.exec(count_stmt).one()
        return [to_domain(r) for r in rows], int(total)

    def update(self, speaker: Speaker) -> Speaker:
        orm = self._s.get(SpeakerORM, speaker.id)
        if orm is None:
            raise SpeakerNotFound(str(speaker.id))
        orm.name = speaker.name
        orm.bio = speaker.bio
        orm.photo_url = speaker.photo_url
        self._s.add(orm)
        self._s.commit()
        self._s.refresh(orm)
        return to_domain(orm)

    def delete(self, speaker_id: int) -> None:
        orm = self._s.get(SpeakerORM, speaker_id)
        if orm is None:
            raise SpeakerNotFound(str(speaker_id))
        self._s.delete(orm)
        self._s.commit()