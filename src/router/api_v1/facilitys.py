from fastapi import APIRouter, Depends, HTTPException, status
from src.router.depandency import SessionDep, get_current_active_user, get_current_active_superuser
from src.service import (
    create_facility_service,
    get_facility_by_id_service,
    delete_facility_service,
    update_facility_service,
    get_all_facilities_service
)
from src.schemas import FacilityCreate, FacilityResponse, FacilityUpdate, FacilityListResponse, PaginationParams
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID  
from typing import Annotated
from src.utils import get_pagination


router = APIRouter(prefix="/api/v1/facilities", tags=["facilities"])

@router.get("/", response_model=list[FacilityResponse])
async def get_facilities(
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    session: SessionDep
):
    return await get_all_facilities_service(session, pagination)

@router.post("/", response_model=FacilityResponse, status_code=201)
async def create_facility(
    facility_in: FacilityCreate,
    db: SessionDep,
    current_user: Annotated[FacilityResponse, Depends(get_current_active_superuser)]
):
    return await create_facility_service(db=db, facility_in=facility_in)

@router.get("/{facility_id}", response_model=FacilityResponse)
async def get_facility_by_id(facility_id: UUID, db: SessionDep):
    return await get_facility_by_id_service(db=db, facility_id=facility_id)

@router.put("/{facility_id}", response_model=FacilityResponse)
async def update_facility(
    facility_id: UUID,
    facility_in: FacilityUpdate,
    db: SessionDep,
    current_user: Annotated[FacilityResponse, Depends(get_current_active_superuser)]
):
    return await update_facility_service(db=db, facility_id=facility_id, facility_in=facility_in)

@router.delete("/{facility_id}", status_code=204)
async def delete_facility(
    facility_id: UUID,
    db: SessionDep,
    current_user: Annotated[FacilityResponse, Depends(get_current_active_superuser)]
):
    await delete_facility_service(db=db, facility_id=facility_id)
    return None



