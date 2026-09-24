from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.schemas.users import OrganizationMembershipResponse, UserCreate, UserResponse


def _user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        organizations=[
            OrganizationMembershipResponse(
                organization_id=m.organization_id,
                role=m.role,
                joined_at=m.joined_at,
            )
            for m in user.memberships
        ],
    )


async def create_user(user: UserCreate, db: AsyncSession) -> UserResponse:
    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password,
        role=user.role,
    )
    for membership in user.organizations:
        new_user.memberships.append(
            OrganizationMember(
                organization_id=membership.organization_id,
                role=membership.role,
            )
        )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user, attribute_names=["memberships"])
    return _user_to_response(new_user)


async def get_user(user_id: UUID, db: AsyncSession) -> UserResponse | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.memberships))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return None
    return _user_to_response(user)
