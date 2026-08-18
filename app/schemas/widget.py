from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WidgetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class WidgetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None


class WidgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    public_key: str
    is_active: bool
    created_at: datetime


class PublicWidgetConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    public_key: str
    is_active: bool
