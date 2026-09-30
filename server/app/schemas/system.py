from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SystemCreate(BaseModel):
    name: str
    description: str | None = None
    system_type: str


class SystemResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    system_type: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)