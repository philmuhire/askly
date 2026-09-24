from datetime import datetime, timedelta, UTC
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.auth import create_access_token, create_refresh_token, verify_token
from app.core.security import hash_password
from app.models.organization_member import OrganizationMember
from app.models.organization import Organization
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.users import (
    OrganizationMembershipResponse,
    RefreshTokenRequest,
    UserCreate,
    UserLogin,
    UserLoginResponse,
    UserResponse,
)
from sqlalchemy import select
from fastapi import HTTPException, status
from app.core.security import verify_password
from app.repositories.user_repository import get_user
import os

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


async def create_user(user: UserCreate, db: AsyncSession) -> UserResponse:
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
    )

    db.add(new_user)
    await db.flush()

    new_org = Organization(
        name=f"{user.email.split('@')[0]}'s Org",
        slug=f"{user.email.split('@')[0]}-org",
        plan="starter",
    )
    db.add(new_org)
    await db.flush()

    new_membership = OrganizationMember(
        user_id=new_user.id, organization_id=new_org.id, role="admin"
    )
    db.add(new_membership)
    await db.flush()

    await db.commit()
    await db.refresh(new_user)
    await db.refresh(new_org)
    await db.refresh(new_membership)

    return UserResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        organizations=[
            OrganizationMembershipResponse(
                organization_id=new_org.id,
                name=new_org.name,
                role=new_membership.role,
                joined_at=new_membership.joined_at,
            )
        ],
    )


async def login(payload: UserLogin, db: AsyncSession) -> UserLoginResponse:

    result = await db.execute(
        select(User)
        .options(selectinload(User.memberships).selectinload(OrganizationMember.organization))
        .where(User.email == payload.email)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    user_id = str(user.id)
    user_email = user.email
    user_name = user.name
    user_orgs = [
        {
            "organization_id": str(o.organization_id),
            "name": o.organization.name,
            "role": o.role,
            "joined_at": o.joined_at.isoformat() if o.joined_at else None,
        }
        for o in user.memberships
    ]

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "type": "access"}
    )
    refresh_token = await create_refresh_token(
        data={"sub": str(user.id), "email": user.email, "type": "refresh"}, db=db
    )

    return UserLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in_days=7,
        user_id=user_id,
        email=user_email,
        name=user_name,
        organizations=user_orgs,
    )


async def get_refresh_token(
    payload: RefreshTokenRequest, db: AsyncSession
) -> UserLoginResponse:
    try:

        decoded = verify_token(payload.refresh_token)
        user_id = decoded.get("sub")
        token_type = decoded.get("type")

        if not user_id or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired or invalid refresh token",
        )

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == refresh_token, RefreshToken.revoked == False
        )
    )

    token_record = result.scalar_one_or_none()

    if token_record:

        user = await get_user(user_id, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired or invalid refresh token",
        )

    # issue new tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "type": "access"}
    )
    refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "id": user.id,
            "type": "refresh",
        }
    )

    return UserLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        name=user.name,
    )
