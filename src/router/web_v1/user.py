
from fastapi import APIRouter, Request, Response, Form
from src.router.depandency import SessionDep, get_current_active_user_from_cookie
from src.service import (
    register_user,
    get_user_profile_service,
    update_user_me_service
)
from src.schemas import UserSignup, Token, UserUpdateMe, UserResponse, UserProfileResponse  
from fastapi import Depends 
from typing import Annotated 
from src.core.security import create_access_token
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates = Jinja2Templates(directory=Path(__file__).parent.parent.parent / "templates")


router = APIRouter(prefix="/web/users", tags=["users"])  

@router.get("/signup")
async def signup_form(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})



@router.post("/signup", status_code=201)
async def signup_user(request: Request, user_in: Annotated[UserSignup, Form()], db: SessionDep):
    new_user = await register_user(db=db, user_in=user_in)
    access_token = create_access_token(data={"user_id": str(new_user.id)})
    response = templates.TemplateResponse("pages/home.html", {"request": request, "current_user": new_user})
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="lax")
    return response

@router.get("/profile")
async def read_users_me(request: Request, current_user: Annotated[UserProfileResponse, Depends(get_current_active_user_from_cookie)]):
    return templates.TemplateResponse("pages/profile.html", {"request": request, "current_user": current_user})


@router.get("/bookings")
async def user_bookings(request: Request, current_user: Annotated[UserProfileResponse, Depends(get_current_active_user_from_cookie)]):
    return templates.TemplateResponse("pages/bookings.html", {"request": request, "current_user": current_user})

    
