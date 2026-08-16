from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.lead import LeadResponse
from app.services.lead import LeadService

router = APIRouter(
    prefix="/leads",
    tags=["leads"],
)


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
)
async def get_lead(
    lead_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> LeadResponse:
    service = LeadService(session)

    lead = await service.get_lead(lead_id)

    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

    return LeadResponse.model_validate(lead)
