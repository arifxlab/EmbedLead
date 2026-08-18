from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.analytics import AnalyticsOverviewResponse
from app.services.analytics import AnalyticsService

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
)
async def get_analytics_overview(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session),
) -> AnalyticsOverviewResponse:
    service = AnalyticsService(session)

    return await service.get_overview(
        tenant_id=current_user.tenant_id,
    )
