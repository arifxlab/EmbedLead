from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.limiter import limiter
from app.db.session import get_db_session
from app.schemas.lead import LeadCreate, PublicLeadResponse
from app.schemas.widget import PublicWidgetConfig
from app.services.geo import GeoService
from app.services.lead import LeadService
from app.services.widget import WidgetService

settings = get_settings()

router = APIRouter(
    prefix="/public",
    tags=["public"],
)


@router.get(
    "/widgets/{public_key}/config",
    response_model=PublicWidgetConfig,
)
async def get_widget_config(
    public_key: str,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> PublicWidgetConfig:
    service = WidgetService(session)

    config = await service.get_public_widget_config(public_key)

    response.headers["Cache-Control"] = (
        f"public, max-age={settings.widget_cache_ttl_seconds}"
    )

    return PublicWidgetConfig.model_validate(config)


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

    if payload.website:
        return PublicLeadResponse(
            message="Lead submitted successfully",
        )

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    geo_metadata = None

    if ip_address:
        geo_service = GeoService(request.app.state.http_client)

        try:
            geo_metadata = await geo_service.lookup(ip_address)
        except Exception:
            geo_metadata = None

    lead_service = LeadService(session)

    lead = await lead_service.create_lead(
        tenant_id=widget.tenant_id,
        widget_id=widget.id,
        name=payload.name,
        email=str(payload.email),
        message=payload.message,
        ip_address=ip_address,
        user_agent=user_agent,
        country=geo_metadata.country if geo_metadata else None,
        region=geo_metadata.region if geo_metadata else None,
        city=geo_metadata.city if geo_metadata else None,
        latitude=geo_metadata.latitude if geo_metadata else None,
        longitude=geo_metadata.longitude if geo_metadata else None,
    )

    return PublicLeadResponse(id=lead.id)
