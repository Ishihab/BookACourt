from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from src.router.depandency import SessionDep, get_user_profile_from_cookie
from src.service import (
    register_user,
    login_user,
    create_user_service,
    update_user_service,
)
from src.schemas import UserSignup, Token, UserUpdateMe, UserResponse, UserProfileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID   
from fastapi.templating import Jinja2Templates
from pathlib import Path


templates = Jinja2Templates(directory=Path(__file__).parent.parent.parent / "templates")



router = APIRouter(prefix="/web", tags=["home"])

@router.get("/")
async def home(request: Request, current_user: Annotated[UserProfileResponse, Depends(get_user_profile_from_cookie)] = None):
    return templates.TemplateResponse("pages/home.html", {"request": request, "current_user": current_user})


@router.get("/book")
async def book_page(request: Request, current_user: Annotated[UserProfileResponse, Depends(get_user_profile_from_cookie)] = None):
    return templates.TemplateResponse("pages/booking.html", {"request": request, "current_user": current_user})


@router.get("/venues")
async def venue_list_page(request: Request, current_user: Annotated[UserProfileResponse, Depends(get_user_profile_from_cookie)] = None):
    return templates.TemplateResponse("pages/venues.html", {"request": request, "current_user": current_user})


@router.get("/venues/{venue_id}")
async def venue_page(venue_id: str, request: Request, current_user: Annotated[UserProfileResponse, Depends(get_user_profile_from_cookie)] = None):
    return templates.TemplateResponse("pages/venue.html", {"request": request, "current_user": current_user, "venue_id": venue_id})
