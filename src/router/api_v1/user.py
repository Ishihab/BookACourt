from fastapi import APIRouter, Request
from src.router.depandency import SessionDep, get_current_active_user, TokenDep
from src.router.service import (
    register_user,
    login_user,
    refresh_user_token,
    update_user_info,
    get_user_profile
)
from src.schemas import UserSignup, Token, UserUpdateMe, UserResponse  
from fastapi import Depends 
from typing import Annotated

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/signup", response_model=UserResponse)
async def signup_user(user_in: UserSignup, db: SessionDep):
    new_user = await register_user(db=db, user_in=user_in)
    return new_user

@router.post("/login", response_model=Token)
async def login_user_endpoint(email: str, password: str, db: SessionDep):
    token = await login_user(db=db, email=email, password=password)
    return token    

@router.post("/refresh-token", response_model=Token | None)
async def refresh_token_endpoint(current_user: Annotated[UserResponse, Depends(get_current_active_user)], db: SessionDep, plain_refresh_token: str = ""):
    new_token = await refresh_user_token(db=db, current_user=current_user, plain_refresh_token=plain_refresh_token)
    return new_token

@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: Annotated[UserResponse, Depends(get_current_active_user)], db: SessionDep):
    user_profile = await get_user_profile(db=db, current_user=current_user)
    return user_profile

@router.put("/me", response_model=UserResponse)
async def update_profile(current_user: Annotated[UserResponse, Depends(get_current_active_user)], user_in: UserUpdateMe, db: SessionDep):
    updated_user = await update_user_info(db=db, current_user=current_user, user_in=user_in)
    return updated_user

