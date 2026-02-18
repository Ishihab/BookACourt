from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.router.depandency import SessionDep, get_current_active_user, TokenDep
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
router = APIRouter(tags=["login"])

@router.post("/login/access-token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep):
    return await login_user(db=db, email=form_data.username, password=form_data.password)

@router.get("/me", response_model=UserProfileResponse)
async def read_users_me(current_user: Annotated[UserProfileResponse, Depends(get_current_active_user)]):
    return current_user 


