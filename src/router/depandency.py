from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.db import AsyncSessionLocal   
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from src.models import Users, refreshTokens
from src.core.security import verify_access_token


oauth2scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2scheme)]

async def get_current_user(token: TokenDep, db: SessionDep) -> Users | None:
    payload = verify_access_token(token)
    if payload is None:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        return None
    result = await db.execute(select(Users).where(Users.id == user_id))
    return result.scalars().first()

async def get_current_active_user(current_user: Annotated[Users | None, Depends(get_current_user)]) -> Users | None:
    if current_user is None or not current_user.is_active:
        return None
    return current_user


async def get_current_active_superuser(current_user: Annotated[Users | None, Depends(get_current_active_user)]) -> Users | None:
    if current_user is None or not current_user.is_superuser:
        return None
    return current_user

