from contextlib import suppress
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import LeadNotFoundError
from app.models.lead import Lead
from app.repositories.lead import LeadRepository
from app.workers.tasks import notify_new_lead


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

        with suppress(Exception):
            notify_new_lead.delay(
                str(lead.id),
                lead.email,
            )

        return lead

    async def get_lead(
        self,
        lead_id: UUID,
        tenant_id: UUID,
    ) -> Lead:
        lead = await self.repository.get_by_id(
            lead_id=lead_id,
            tenant_id=tenant_id,
        )

        if lead is None:
            raise LeadNotFoundError

        return lead

    async def list_leads(
        self,
        tenant_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[Lead], int, int]:
        leads, total = await self.repository.list_by_tenant(
            tenant_id=tenant_id,
            page=page,
            page_size=page_size,
        )

        pages = (total + page_size - 1) // page_size

        return leads, total, pages

    async def get_widget_leads(
        self,
        widget_id: UUID,
        tenant_id: UUID,
    ) -> list[Lead]:
        return await self.repository.get_by_widget_id(
            widget_id=widget_id,
            tenant_id=tenant_id,
        )
