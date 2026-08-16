from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.widget import WidgetCreate, WidgetResponse
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
    session: AsyncSession = Depends(get_db_session),
) -> WidgetResponse:
    service = WidgetService(session)

    widget = await service.create_widget(
        tenant_id=payload.tenant_id,
        name=payload.name,
        public_key=payload.public_key,
    )

    return WidgetResponse.model_validate(widget)


@router.get(
    "/{widget_id}",
    response_model=WidgetResponse,
)
async def get_widget(
    widget_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> WidgetResponse:
    service = WidgetService(session)

    widget = await service.get_widget(widget_id)

    return WidgetResponse.model_validate(widget)
