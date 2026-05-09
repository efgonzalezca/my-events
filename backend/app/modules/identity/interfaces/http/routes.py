from fastapi import APIRouter

from app.modules.identity.application.dtos import LoginCmd, RegisterUserCmd
from app.modules.identity.application.use_cases import (
    get_me,
    login,
    register_user,
)
from app.modules.identity.interfaces.http.deps import (
    CurrentUserId,
    HasherDep,
    TokensDep,
    UserRepoDep,
)
from app.modules.identity.interfaces.http.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
def register(req: RegisterRequest, repo: UserRepoDep, hasher: HasherDep) -> UserResponse:
    dto = register_user(
        RegisterUserCmd(req.email, req.password, req.full_name),
        repo,
        hasher,
    )
    return UserResponse(**dto.__dict__)


@router.post("/login", response_model=TokenResponse)
def login_route(
    req: LoginRequest,
    repo: UserRepoDep,
    hasher: HasherDep,
    tokens: TokensDep,
) -> TokenResponse:
    dto = login(LoginCmd(req.email, req.password), repo, hasher, tokens)
    return TokenResponse(**dto.__dict__)


@router.get("/me", response_model=UserResponse)
def me(user_id: CurrentUserId, repo: UserRepoDep) -> UserResponse:
    return UserResponse(**get_me(user_id, repo).__dict__)
