from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.limiter import limiter
from app.db.session import get_db_session
from app.schemas.lead import LeadCreate, PublicLeadResponse
from app.services.lead import LeadService
from app.services.widget import WidgetService

settings = get_settings()

router = APIRouter(
    prefix="/public",
    tags=["public"],
)


@router.post(
    "/widgets/{public_key}/leads",
    response_model=PublicLeadResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(lambda: f"{settings.rate_limit_per_minute}/minute")
async def submit_lead(
    request: Request,
    public_key: str,
    payload: LeadCreate,
    session: AsyncSession = Depends(get_db_session),
) -> PublicLeadResponse:
    widget_service = WidgetService(session)
    widget = await widget_service.get_public_widget(public_key)

    lead_service = LeadService(session)

    lead = await lead_service.create_lead(
        tenant_id=widget.tenant_id,
        widget_id=widget.id,
        name=payload.name,
        email=str(payload.email),
        message=payload.message,
    )

    return PublicLeadResponse(id=lead.id)
