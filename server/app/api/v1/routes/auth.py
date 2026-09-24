from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import verify_token

from app.db.main import get_db
from app.repositories import user_repository
from app.schemas.users import RefreshTokenRequest, UserCreate, UserLogin, UserLoginResponse, UserResponse
from app.services import user as user_service

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@auth_router.post("/", response_model=UserResponse)
async def create_user_endpoint(
    user: UserCreate, db: AsyncSession = Depends(get_db)
):
    return await user_service.create_user(user, db)

@auth_router.post("/signin", response_model = UserLoginResponse)
async def login_endpoint(
    payload: UserLogin, db: AsyncSession = Depends(get_db)
):
    return await user_service.login(payload, db) 


@auth_router.post("/refresh", response_model = UserLoginResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
): 
    return await user_service.get_refresh_token(payload, db)