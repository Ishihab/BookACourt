from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Response
from src.router.depandency import SessionDep
from src.service import (
    register_user,
    login_user,
    create_user_service,
    update_user_service,
    get_user_profile_service

)
from src.core.security import create_access_token
from src.schemas import UserSignup, Token, UserUpdateMe, UserResponse, UserProfileResponse, UserLogin
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID  
from typing import Annotated
from fastapi.templating import Jinja2Templates
from pathlib import Path    

templates = Jinja2Templates(directory=Path(__file__).parent.parent.parent / "templates")

router = APIRouter(prefix="/web", tags=["login"])

@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
async def login_for_access_token(request: Request, response: Response, form_data: Annotated[UserLogin, Form()], db: SessionDep):
    login_result = await login_user(db=db, email=form_data.email, password=form_data.password)
    print("Login result:", login_result)
    user = await get_user_profile_service(db=db, email=form_data.email)
    print("User profile:", user)
    template_response = templates.TemplateResponse("pages/home.html", {"request": request, "current_user": user})
    template_response.set_cookie(key="access_token", value=login_result["access_token"], httponly=True, secure=True, samesite="lax")
    print("Access token set in cookie:", login_result["access_token"])
    return template_response


@router.get("/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get("access_token")
    print("Token to be deleted:", token)
    template_response = templates.TemplateResponse("auth/login.html", {"request": request})
    template_response.delete_cookie(key="access_token")
    return template_response