from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Users, Facilities, refreshTokens
from src.core.security import verify_password, hash_refresh_token, create_refresh_token, create_access_token
from src.core.config import settings
from datetime import datetime, timezone, timedelta
from typing import Any




async def create_user(db: AsyncSession, user: Users) -> Users:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_email(db: AsyncSession, email: str) -> Users | None:
    result = await db.execute(select(Users).where(Users.email == email))
    return result.scalars().first()

async def update_user(db: AsyncSession, user: Users) -> Users:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

DUMMY_HASH = "$argon2id$v=19$m=16,t=2,p=1$cmVkczU0NWprbGR2ZGY$aJSdOU9rCKtXYEAClPoAug"


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Users | None:
    result = await db.execute(select(Users).where(Users.email == email))
    user = result.scalars().first()
    if user is None:
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def refresh_access_token(db: AsyncSession, user: Users, plain_refresh_token: str) -> Any:
    if plain_refresh_token == "":
        return None
    hashed_token = hash_refresh_token(plain_refresh_token)
    result = await db.execute(
        select(refreshTokens).where(
            refreshTokens.user_id == user.id,
            refreshTokens.hashed_token == hashed_token,
            refreshTokens.expire_at > func.now()
        )
    )
    token_entry = result.scalars().first()
    if token_entry is None:
        return None
    
    new_refresh_token = create_refresh_token()
    token_entry.hashed_token = hash_refresh_token(new_refresh_token)
    token_entry.expire_at = func.now() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(data={"sub": str(user.id)})
    return new_access_token


async def create_refresh_token_entry(db: AsyncSession, user: Users, plain_refresh_token: str) -> refreshTokens:
    hashed_token = hash_refresh_token(plain_refresh_token)
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    token_entry = refreshTokens(
        user_id=user.id,
        hashed_token=hashed_token,
        expire_at=expire_at
    )
    db.add(token_entry)
    await db.commit()
    await db.refresh(token_entry)
    return token_entry

async def revoke_refresh_token(db: AsyncSession, user: Users, plain_refresh_token: str) -> None:
    hashed_token = hash_refresh_token(plain_refresh_token)
    result = await db.execute(
        select(refreshTokens).where(
            refreshTokens.user_id == user.id,
            refreshTokens.hashed_token == hashed_token
        )
    )
    token_entry = result.scalars().first()
    if token_entry:
        await db.delete(token_entry)
        await db.commit()





