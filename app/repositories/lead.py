from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead


class LeadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        tenant_id: UUID,
        widget_id: UUID,
        name: str | None,
        email: str,
        message: str | None,
    ) -> Lead:
        lead = Lead(
            tenant_id=tenant_id,
            widget_id=widget_id,
            name=name,
            email=email,
            message=message,
        )

        self.session.add(lead)
        await self.session.flush()

        return lead

    async def get_by_id(
        self,
        lead_id: UUID,
    ) -> Lead | None:
        result = await self.session.execute(select(Lead).where(Lead.id == lead_id))

        return result.scalar_one_or_none()

    async def get_by_widget_id(
        self,
        widget_id: UUID,
    ) -> list[Lead]:
        result = await self.session.execute(
            select(Lead).where(Lead.widget_id == widget_id).order_by(Lead.created_at.desc())
        )

        return list(result.scalars().all())
