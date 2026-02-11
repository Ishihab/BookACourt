from src.router.api_v1 import user as api_v1_user
from fastapi import APIRouter


router = APIRouter()

router.include_router(api_v1_user.router)



