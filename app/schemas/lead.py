from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LeadCreate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr
    message: str | None = Field(default=None, max_length=5000)
    website: str | None = Field(default=None, max_length=255)


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    widget_id: UUID
    name: str | None
    email: EmailStr
    message: str | None
    created_at: datetime
    updated_at: datetime


class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    page: int
    page_size: int
    total: int
    pages: int


class PublicLeadResponse(BaseModel):
    id: UUID | None = None
    message: str = "Lead submitted successfully"
