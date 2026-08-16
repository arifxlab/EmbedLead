from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.repositories.lead import LeadRepository


class LeadService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = LeadRepository(session)

    async def create_lead(
        self,
        tenant_id: UUID,
        widget_id: UUID,
        name: str | None,
        email: str,
        message: str | None,
    ) -> Lead:
        lead = await self.repository.create(
            tenant_id=tenant_id,
            widget_id=widget_id,
            name=name,
            email=email,
            message=message,
        )

        await self.session.commit()
        await self.session.refresh(lead)

        return lead

    async def get_lead(
        self,
        lead_id: UUID,
    ) -> Lead | None:
        return await self.repository.get_by_id(lead_id)

    async def get_widget_leads(
        self,
        widget_id: UUID,
    ) -> list[Lead]:
        return await self.repository.get_by_widget_id(widget_id)
