from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.db import AsyncSessionLocal   
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from src.models import Users
from src.core.security import verify_access_token
from fastapi import HTTPException, status, Request
from src.crud import get_user_by_id




oauth2scheme = OAuth2PasswordBearer(tokenUrl="login/access-token")



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2scheme)]







async def get_current_user(
    token: TokenDep,
    db: SessionDep
) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_access_token(token)
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Users = Depends(get_current_user)
) -> Users:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user

async def get_current_active_superuser(
    current_user: Users = Depends(get_current_active_user)
) -> Users:
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges")
    return current_user


async def get_current_active_user_from_cookie(request: Request, db: SessionDep) -> Users:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated",
            headers={"Location": "/web/login"},)
    try:
        payload = verify_access_token(token)
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Could not validate credentials",
                headers={"Location": "/web/login"},)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Could not validate credentials",
            headers={"Location": "/web/login"},)
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Could not validate credentials",
            headers={"Location": "/web/login"},)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Inactive user",
            headers={"Location": "/web/user_inactive"},)
    return user


async def get_user_profile_from_cookie(request: Request, db: SessionDep) -> Users:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = verify_access_token(token)
        user_id: str = payload.get("user_id")
        if user_id is None:
            return None
    except Exception:
        return None
    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        return None
    return user