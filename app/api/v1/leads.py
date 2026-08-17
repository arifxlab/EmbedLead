from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.lead import LeadListResponse, LeadResponse
from app.services.lead import LeadService

router = APIRouter(
    prefix="/leads",
    tags=["leads"],
)


@router.get(
    "",
    response_model=LeadListResponse,
)
async def list_leads(
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> LeadListResponse:
    service = LeadService(session)

    leads, total, pages = await service.list_leads(
        tenant_id=current_user.tenant_id,
        page=page,
        page_size=page_size,
    )

    return LeadListResponse(
        items=[LeadResponse.model_validate(lead) for lead in leads],
        page=page,
        page_size=page_size,
        total=total,
        pages=pages,
    )


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
)
async def get_lead(
    lead_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session),
) -> LeadResponse:
    service = LeadService(session)

    lead = await service.get_lead(
        lead_id=lead_id,
        tenant_id=current_user.tenant_id,
    )

    return LeadResponse.model_validate(lead)
