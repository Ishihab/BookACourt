from src.router.api_v1 import login as api_v1_auth
from src.router.api_v1 import user as api_v1_user
from src.router.web_v1 import login as web_v1_auth
from src.router.web_v1 import user as web_v1_user
from src.router.web_v1 import home as web_v1_home
from src.router.api_v1 import facilitys as api_v1_facilitys
from src.router.api_v1 import resource as api_v1_resource
from src.router.api_v1 import bookings as api_v1_bookings
from fastapi import APIRouter



router = APIRouter()

router.include_router(api_v1_auth.router)
router.include_router(api_v1_user.router)
router.include_router(web_v1_auth.router)
router.include_router(web_v1_user.router)
router.include_router(web_v1_home.router)
router.include_router(api_v1_facilitys.router)
router.include_router(api_v1_resource.router)
router.include_router(api_v1_bookings.router)   






