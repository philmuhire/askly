from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrganizationMembershipInput(BaseModel):
    organization_id: UUID
    role: str = "member"


class OrganizationMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    organization_id: UUID
    name: Optional[str] = None
    role: str
    joined_at: datetime


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    organizations: list[OrganizationMembershipResponse]


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    role: str | None = None
    is_active: bool | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserLoginResponse(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str
    token_type: str
    expires_in_days: int
    name: str
    email: str
    organizations: list[OrganizationMembershipResponse]


class UserLogoutResponse(BaseModel):
    message: str
