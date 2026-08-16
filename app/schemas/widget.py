from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WidgetCreate(BaseModel):
    tenant_id: UUID
    name: str
    public_key: str


class WidgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    public_key: str
    is_active: bool
    created_at: datetime
