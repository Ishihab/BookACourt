from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.router.depandency import SessionDep
from src.router.service import login_user
from src.schemas import Token
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep
):
    token = await login_user(db=db, email=form_data.username, password=form_data.password)
    return token
