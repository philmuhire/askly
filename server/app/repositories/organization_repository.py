from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate


async def create_organization(
    organization: OrganizationCreate, db: AsyncSession
) -> Organization:
    new_organization = Organization(
        name=organization.name,
        slug=organization.slug,
        plan=organization.plan,
    )
    db.add(new_organization)
    await db.commit()
    await db.refresh(new_organization)
    return new_organization


async def get_organization(
    organization_id: UUID, db: AsyncSession
) -> Organization | None:
    result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    return result.scalar_one_or_none()


async def get_organizations(db: AsyncSession) -> list[Organization]:
    result = await db.execute(select(Organization))
    return list(result.scalars().all())
