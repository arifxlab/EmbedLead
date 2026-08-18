from datetime import date

from pydantic import BaseModel


class AnalyticsBreakdownItem(BaseModel):
    name: str
    count: int


class AnalyticsDailyCount(BaseModel):
    date: date
    count: int


class AnalyticsOverviewResponse(BaseModel):
    total_leads: int
    leads_today: int
    leads_this_week: int
    leads_this_month: int
    countries: list[AnalyticsBreakdownItem]
    cities: list[AnalyticsBreakdownItem]
    daily_leads: list[AnalyticsDailyCount]
