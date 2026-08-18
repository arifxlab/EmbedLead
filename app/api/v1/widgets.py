from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.widget import WidgetCreate, WidgetResponse
from app.schemas.widget_embed import WidgetEmbedResponse
from app.services.widget import WidgetService

router = APIRouter(
    prefix="/widgets",
    tags=["widgets"],
)


@router.post(
    "",
    response_model=WidgetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_widget(
    payload: WidgetCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session),
) -> WidgetResponse:
    service = WidgetService(session)

    widget = await service.create_widget(
        tenant_id=current_user.tenant_id,
        name=payload.name,
    )

    return WidgetResponse.model_validate(widget)


@router.get(
    "/{widget_id}",
    response_model=WidgetResponse,
)
async def get_widget(
    widget_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session),
) -> WidgetResponse:
    service = WidgetService(session)

    widget = await service.get_widget(
        widget_id=widget_id,
        tenant_id=current_user.tenant_id,
    )

    return WidgetResponse.model_validate(widget)


@router.get(
    "/{widget_id}/embed",
    response_model=WidgetEmbedResponse,
)
async def get_widget_embed(
    widget_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session),
) -> WidgetEmbedResponse:
    service = WidgetService(session)

    widget = await service.get_widget(
        widget_id=widget_id,
        tenant_id=current_user.tenant_id,
    )

    embed_snippet = (
        f'<script src="http://127.0.0.1:8000/api/v1/widget.v1.js?key={widget.public_key}"></script>'
    )

    return WidgetEmbedResponse(
        widget_id=str(widget.id),
        public_key=widget.public_key,
        embed_snippet=embed_snippet,
    )
