from fastapi import APIRouter, Depends, HTTPException, status
from src.router.depandency import SessionDep, get_current_active_user, get_current_active_superuser
from src.service import (
    create_booking_service,
    get_booking_by_id_service,
    delete_booking_service,
    update_booking_service,
    get_bookings_by_user_id_service,
    get_bookings_by_resource_id_service,
    get_bookings_by_facility_id_service,
    get_all_bookings_service
)
from src.schemas import BookingCreate, BookingResponse, BookingUpdate, PaginationParams, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID  
from typing import Annotated
from src.utils import get_pagination    

router = APIRouter(prefix="/api/v1/bookings", tags=["bookings"])

@router.post("/{facility_id}", response_model=BookingResponse, status_code=201)
async def create_booking(
    booking_in: BookingCreate,
    facility_id: UUID,
    db: SessionDep,
    current_user: Annotated[BookingResponse, Depends(get_current_active_user)]
):
    return await create_booking_service(db=db, booking_in=booking_in, user_id=current_user.id, facility_id=facility_id)

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking_by_id(booking_id: UUID, db: SessionDep, current_user: Annotated[UserResponse, Depends(get_current_active_user)]):
    return await get_booking_by_id_service(db=db, booking_id=booking_id, current_user=current_user)

@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: UUID,
    booking_in: BookingUpdate,
    db: SessionDep,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    booking_data = await get_booking_by_id_service(db=db, booking_id=booking_id, current_user=current_user)
    if booking_data is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking_data.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=404, detail="Booking not found")
    return await update_booking_service(db=db, booking_id=booking_id, booking_in=booking_in)

@router.delete("/{booking_id}", status_code=204)
async def delete_booking(
    booking_id: UUID,
    db: SessionDep,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    booking_data = await get_booking_by_id_service(db=db, booking_id=booking_id, current_user=current_user)
    if booking_data is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking_data.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=404, detail="Booking not found")
    await delete_booking_service(db=db, booking_id=booking_id)
    return None

@router.get("/user/{user_id}", response_model=list[BookingResponse])
async def get_bookings_by_user_id(
    user_id: UUID,
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    db: SessionDep,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await get_bookings_by_user_id_service(db=db, user_id=user_id, pagination=pagination)

@router.get("/resource/{resource_id}", response_model=list[BookingResponse])
async def get_bookings_by_resource_id(
    resource_id: UUID,
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    db: SessionDep,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    return await get_bookings_by_resource_id_service(db=db, resource_id=resource_id, pagination=pagination)

@router.get("/facility/{facility_id}", response_model=list[BookingResponse])
async def get_bookings_by_facility_id(
    facility_id: UUID,
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    db: SessionDep,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    return await get_bookings_by_facility_id_service(db=db, facility_id=facility_id, pagination=pagination)

@router.get("/", response_model=list[BookingResponse])
async def get_all_bookings(
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    db: SessionDep,
    current_user: Annotated[UserResponse, Depends(get_current_active_superuser)]
):
    return await get_all_bookings_service(db=db, pagination=pagination)

