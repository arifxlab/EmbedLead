from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analytics import AnalyticsRepository
from app.schemas.analytics import (
    AnalyticsBreakdownItem,
    AnalyticsDailyCount,
    AnalyticsOverviewResponse,
)


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = AnalyticsRepository(session)

    async def get_overview(
        self,
        tenant_id: UUID,
    ) -> AnalyticsOverviewResponse:
        now = datetime.now(UTC)

        today_start = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        week_start = today_start - timedelta(days=today_start.weekday())

        month_start = today_start.replace(
            day=1,
        )

        daily_start = today_start - timedelta(days=29)

        total_leads = await self.repository.count_total_leads(
            tenant_id=tenant_id,
        )

        leads_today = await self.repository.count_leads_since(
            tenant_id=tenant_id,
            start=today_start,
        )

        leads_this_week = await self.repository.count_leads_since(
            tenant_id=tenant_id,
            start=week_start,
        )

        leads_this_month = await self.repository.count_leads_since(
            tenant_id=tenant_id,
            start=month_start,
        )

        countries = await self.repository.count_by_country(
            tenant_id=tenant_id,
        )

        cities = await self.repository.count_by_city(
            tenant_id=tenant_id,
        )

        daily_counts = await self.repository.count_daily(
            tenant_id=tenant_id,
            start=daily_start,
            end=today_start + timedelta(days=1),
        )

        return AnalyticsOverviewResponse(
            total_leads=total_leads,
            leads_today=leads_today,
            leads_this_week=leads_this_week,
            leads_this_month=leads_this_month,
            countries=[
                AnalyticsBreakdownItem(
                    name=name,
                    count=count,
                )
                for name, count in countries
            ],
            cities=[
                AnalyticsBreakdownItem(
                    name=name,
                    count=count,
                )
                for name, count in cities
            ],
            daily_leads=[
                AnalyticsDailyCount(
                    date=lead_date,
                    count=count,
                )
                for lead_date, count in daily_counts
            ],
        )
