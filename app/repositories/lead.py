from uuid import UUID

from sqlalchemy import func, select
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
        ip_address: str | None = None,
        user_agent: str | None = None,
        country: str | None = None,
        region: str | None = None,
        city: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> Lead:
        lead = Lead(
            tenant_id=tenant_id,
            widget_id=widget_id,
            name=name,
            email=email,
            message=message,
            ip_address=ip_address,
            user_agent=user_agent,
            country=country,
            region=region,
            city=city,
            latitude=latitude,
            longitude=longitude,
        )

        self.session.add(lead)
        await self.session.flush()

        return lead

    async def get_by_id(
        self,
        lead_id: UUID,
        tenant_id: UUID,
    ) -> Lead | None:
        result = await self.session.execute(
            select(Lead).where(
                Lead.id == lead_id,
                Lead.tenant_id == tenant_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_widget_id(
        self,
        widget_id: UUID,
        tenant_id: UUID,
    ) -> list[Lead]:
        result = await self.session.execute(
            select(Lead)
            .where(
                Lead.widget_id == widget_id,
                Lead.tenant_id == tenant_id,
            )
            .order_by(Lead.created_at.desc(), Lead.id.desc())
        )

        return list(result.scalars().all())

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[Lead], int]:
        offset = (page - 1) * page_size

        result = await self.session.execute(
            select(Lead)
            .where(Lead.tenant_id == tenant_id)
            .order_by(Lead.created_at.desc(), Lead.id.desc())
            .offset(offset)
            .limit(page_size)
        )

        count_result = await self.session.execute(
            select(func.count()).select_from(Lead).where(Lead.tenant_id == tenant_id)
        )

        total = count_result.scalar_one()

        return list(result.scalars().all()), total
