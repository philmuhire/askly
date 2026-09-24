from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.main import get_db
from app.repositories import organization_repository
from app.schemas.organization import OrganizationCreate, OrganizationResponse

organization_router = APIRouter(
    prefix="/organizations",
    tags=["organizations"],
)

@organization_router.post("/", response_model=OrganizationResponse)
async def create_organization_endpoint(
    organization: OrganizationCreate, db: AsyncSession = Depends(get_db)
):
    return await organization_repository.create_organization(organization, db)


@organization_router.get("/", response_model=List[OrganizationResponse])
async def list_organizations_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await organization_repository.get_organizations(db)


@organization_router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization_endpoint(
    organization_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await organization_repository.get_organization(organization_id, db)






