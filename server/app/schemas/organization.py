from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class OrganizationCreate(BaseModel):
    name: str
    slug: str
    plan: str

class OrganizationUpdate(BaseModel):
    name: str
    slug: str
    plan: str

class OrganizationDelete(BaseModel):
    id: UUID

class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    plan: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

