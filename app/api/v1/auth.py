from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    service = AuthService(session)

    user = await service.register_user(
        tenant_id=payload.tenant_id,
        email=str(payload.email),
        password=payload.password,
    )

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    service = AuthService(session)

    user = await service.authenticate_user(
        email=str(payload.email),
        password=payload.password,
    )

    access_token = service.create_access_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
    )

    return TokenResponse(access_token=access_token)
