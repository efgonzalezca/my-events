from fastapi import APIRouter, Query

from app.interfaces.http.auth import require_role
from app.modules.identity.application.dtos import UserDTO
from app.modules.identity.domain.entities import UserRole
from app.modules.speakers.application.dtos import CreateSpeakerCmd
from app.modules.speakers.application.use_cases import (
    create_speaker,
    get_speaker,
    list_speakers,
)
from app.modules.speakers.interfaces.http.deps import SpeakerRepoDep
from app.modules.speakers.interfaces.http.schemas import (
    PaginatedSpeakersResponse,
    SpeakerCreateRequest,
    SpeakerResponse,
)

router = APIRouter()


@router.post("", response_model=SpeakerResponse, status_code=201)
def create_speaker_route(
    req: SpeakerCreateRequest,
    repo: SpeakerRepoDep,
    _me: UserDTO = require_role(UserRole.organizer, UserRole.admin),
) -> SpeakerResponse:
    cmd = CreateSpeakerCmd(
        name=req.name,
        bio=req.bio,
        photo_url=req.photo_url,
    )
    dto = create_speaker(cmd, repo=repo)
    return SpeakerResponse(**dto.__dict__)


@router.get("", response_model=PaginatedSpeakersResponse)
def list_speakers_route(
    repo: SpeakerRepoDep,
    q: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> PaginatedSpeakersResponse:
    dto = list_speakers(q=q, page=page, size=size, repo=repo)
    return PaginatedSpeakersResponse(
        items=[SpeakerResponse(**s.__dict__) for s in dto.items],
        page=dto.page,
        size=dto.size,
        total=dto.total,
    )


@router.get("/{speaker_id}", response_model=SpeakerResponse)
def get_speaker_route(speaker_id: int, repo: SpeakerRepoDep) -> SpeakerResponse:
    dto = get_speaker(speaker_id, repo)
    return SpeakerResponse(**dto.__dict__)