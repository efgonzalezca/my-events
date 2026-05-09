from fastapi import APIRouter

from app.interfaces.http.auth import require_role
from app.modules.identity.application.dtos import UserDTO
from app.modules.identity.domain.entities import UserRole
from app.modules.speakers.application.dtos import CreateSpeakerCmd
from app.modules.speakers.application.use_cases import create_speaker
from app.modules.speakers.interfaces.http.deps import SpeakerRepoDep
from app.modules.speakers.interfaces.http.schemas import (
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