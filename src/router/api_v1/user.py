from fastapi import APIRouter, Depends, HTTPException, status
from src.router.depandency import SessionDep, get_current_active_user
from src.service import (
    register_user,
    login_user,
    create_user_service,
    update_user_service,
)
from src.schemas import UserSignup, Token, UserUpdateMe, UserResponse, UserProfileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID  
from typing import Annotated



router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/signup", response_model=UserProfileResponse, status_code=201)
async def signup_user(user_in: UserSignup, db: SessionDep):
    return await register_user(db=db, user_in=user_in)



