from src.crud import (
    create_user,
    get_user_by_email,
    update_user,
    authenticate_user,
    refresh_access_token,
    create_refresh_token_entry
)
from src.core.security import (
    hash_password,
    verify_password,
    hash_refresh_token,
    create_refresh_token,
    create_access_token
)
from src.core.config import settings
from src.schemas import UserCreate, UserUpdate, Token, TokenData, UserResponse, UserSignup
from src.models import Users
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status


async def register_user(db: AsyncSession, user_in: UserSignup | UserCreate) -> UserResponse:
    user = await get_user_by_email(email=user_in.email, db=db)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
    hashed_password = hash_password(user_in.password)
    new_user = Users(
        email=user_in.email,
        full_name=getattr(user_in, 'full_name', None),
        hashed_password=hashed_password,
        is_active=getattr(user_in, 'is_active', True),
        is_superuser=getattr(user_in, 'is_superuser', False)
    )
    created_user = await create_user(db=db, user=new_user)
    return UserResponse.model_validate(created_user)

async def login_user(db: AsyncSession, email: str, password: str) -> Token:
    user = await authenticate_user(db=db, email=email, password=password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token()
    await create_refresh_token_entry(db=db, user=user, plain_refresh_token=refresh_token)
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

async def refresh_user_token(db: AsyncSession, current_user: UserResponse, plain_refresh_token: str) -> Token | None:
    user = await get_user_by_email(db=db, email=current_user.email)
    if not user:
        return None
    new_access_token = await refresh_access_token(db=db, user=user, plain_refresh_token=plain_refresh_token)
    if not new_access_token:
        return None
    new_refresh_token = create_refresh_token()
    await create_refresh_token_entry(db=db, user=user, plain_refresh_token=new_refresh_token)
    return Token(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")

async def update_user_info(db: AsyncSession, current_user: UserResponse, user_in: UserUpdate) -> UserResponse:
    user = await get_user_by_email(db=db, email=current_user.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user_in.email and user_in.email != user.email:
        existing_user = await get_user_by_email(db=db, email=user_in.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    if user_in.password:
        user.hashed_password = hash_password(user_in.password)
    if user_in.email:
        user.email = user_in.email
    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.is_superuser is not None:
        user.is_superuser = user_in.is_superuser
    updated_user = await update_user(db=db, user=user)
    return UserResponse.model_validate(updated_user)

async def get_user_profile(db: AsyncSession, current_user: UserResponse) -> UserResponse:
    user = await get_user_by_email(db=db, email=current_user.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)




