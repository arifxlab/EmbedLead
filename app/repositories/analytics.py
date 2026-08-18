from datetime import date, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead


class AnalyticsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count_total_leads(
        self,
        tenant_id: UUID,
    ) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Lead)
            .where(Lead.tenant_id == tenant_id)
        )

        return result.scalar_one()

    async def count_leads_since(
        self,
        tenant_id: UUID,
        start: datetime,
    ) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Lead)
            .where(
                Lead.tenant_id == tenant_id,
                Lead.created_at >= start,
            )
        )

        return result.scalar_one()

    async def count_by_country(
        self,
        tenant_id: UUID,
    ) -> list[tuple[str, int]]:
        result = await self.session.execute(
            select(
                Lead.country,
                func.count().label("count"),
            )
            .where(
                Lead.tenant_id == tenant_id,
                Lead.country.is_not(None),
            )
            .group_by(Lead.country)
            .order_by(func.count().desc(), Lead.country.asc())
        )

        return [
            (country, count)
            for country, count in result.all()
            if country is not None
        ]

    async def count_by_city(
        self,
        tenant_id: UUID,
    ) -> list[tuple[str, int]]:
        result = await self.session.execute(
            select(
                Lead.city,
                func.count().label("count"),
            )
            .where(
                Lead.tenant_id == tenant_id,
                Lead.city.is_not(None),
            )
            .group_by(Lead.city)
            .order_by(func.count().desc(), Lead.city.asc())
        )

        return [
            (city, count)
            for city, count in result.all()
            if city is not None
        ]

    async def count_daily(
        self,
        tenant_id: UUID,
        start: datetime,
        end: datetime,
    ) -> list[tuple[date, int]]:
        day = func.date(Lead.created_at)

        result = await self.session.execute(
            select(
                day.label("date"),
                func.count().label("count"),
            )
            .where(
                Lead.tenant_id == tenant_id,
                Lead.created_at >= start,
                Lead.created_at < end,
            )
            .group_by(day)
            .order_by(day.asc())
        )

        return [
            (lead_date, count)
            for lead_date, count in result.all()
            if isinstance(lead_date, date)
        ]
