from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.organizations import Organization
from app.schemas.organization import OrganizationCreate

async def create_organization(organization: OrganizationCreate, db: AsyncSession) -> Organization:
    new_organization = Organization(
        name=organization.name,
        slug=organization.slug,
        plan=organization.plan,
    )
    db.add(new_organization)
    await db.commit()
    await db.refresh(new_organization)