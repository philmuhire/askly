from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import verify_token

from app.db.main import get_db
from app.repositories import user_repository
from app.schemas.users import RefreshTokenRequest, UserCreate, UserLogin, UserLoginResponse, UserResponse
from app.services import user

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@users_router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(
    user_id: UUID, db: AsyncSession = Depends(get_db)
):
    user = await user_repository.get_user(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
