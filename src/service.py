import src.crud as crud
from src.schemas import (
    UserSignup, 
    UserUpdate, 
    UserUpdateMe, 
    UserResponse,
    UserCreate,
    UserProfileResponse,
    FacilityCreate, 
    FacilityUpdate, 
    FacilityResponse,
    ResourceCreate, 
    ResourceUpdate, 
    ResourceResponse,
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    PaginationParams
)
from src.core.security import create_access_token
from src.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import timedelta
from fastapi import HTTPException, status  
from src.utils import get_pagination, calculate_total_price
 



async def register_user(db: AsyncSession, user_in: UserSignup) -> dict:
    existing_user = await crud.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    new_user = await crud.create_user(db, user_in)
    return new_user

async def login_user(db: AsyncSession, email: str, password: str) -> dict:
    user = await crud.authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user."
        )
    access_token = create_access_token(data={"user_id": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

async def create_user_service(db: AsyncSession, user_in: UserCreate) -> UserResponse:
    existing_user = await crud.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    new_user = await crud.create_user(db, user_in)
    return UserResponse.model_validate(new_user)

async def update_user_service(db: AsyncSession, user_id: UUID, user_in: UserUpdate) -> UserResponse:
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    if user_in.email:
        existing_user = await crud.get_user_by_email(db, user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered to another user."
            )
    updated_user = await crud.update_user(db, user, user_in)
    return UserResponse.model_validate(updated_user)

async def update_user_me_service(db: AsyncSession, current_user: UserProfileResponse, user_in: UserUpdateMe) -> UserProfileResponse:
    if user_in.email:
        existing_user = await crud.get_user_by_email(db, user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered to another user."
            )
    user = await crud.get_user_by_id(db, current_user.id)
    updated_user = await crud.update_user_me(db, user, user_in)
    return UserProfileResponse.model_validate(updated_user)

async def get_user_profile_service(db: AsyncSession, email: str) -> UserProfileResponse:
    user = await crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return UserProfileResponse.model_validate(user)

async def get_all_users_service(db: AsyncSession, pagination: PaginationParams) -> list[UserResponse]:
    offset = (pagination.page - 1) * pagination.page_size
    limit = pagination.page_size
    users = await crud.get_all_users(db, limit=limit, offset=offset)
    return [UserResponse.model_validate(user) for user in users]

async def get_user_by_id_service(db: AsyncSession, user_id: UUID) -> UserResponse:
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return UserResponse.model_validate(user)

async def create_facility_service(db: AsyncSession, facility_in: FacilityCreate) -> FacilityResponse:
    existing_facility = await crud.get_facility_by_name_city(db, facility_in.name, facility_in.city)
    if existing_facility:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Facility with the same name already exists in the city."
        )
    new_facility = await crud.create_facility(db, facility_in)
    return FacilityResponse.model_validate(new_facility)

async def get_facility_by_id_service(db: AsyncSession, facility_id: UUID) -> FacilityResponse:
    facility = await crud.get_facility_by_id(db, facility_id)
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found."
        )
    return FacilityResponse.model_validate(facility)


async def get_all_facilities_service(db: AsyncSession, pagination: PaginationParams) -> list[FacilityResponse]:
    offset = (pagination.page - 1) * pagination.page_size
    limit = pagination.page_size
    facilities = await crud.get_all_facilities(db, limit=limit, offset=offset)
    return [FacilityResponse.model_validate(facility) for facility in facilities]

async def delete_facility_service(db: AsyncSession, facility_id: UUID):
    facility = await crud.get_facility_by_id(db, facility_id)
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found."
        )
    await crud.delete_facility(db, facility)    


async def update_facility_service(db: AsyncSession, facility_id: UUID, facility_in: FacilityUpdate) -> FacilityResponse:
    facility = await crud.get_facility_by_id(db, facility_id)
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found."
        )
    if facility_in.name and facility_in.city:
        existing_facility = await crud.get_facility_by_name_city(db, facility_in.name, facility_in.city)
        if existing_facility and existing_facility.id != facility_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Facility with the same name already exists in the city."
            )
    updated_facility = await crud.update_facility(db, facility, facility_in)
    return FacilityResponse.model_validate(updated_facility)


async def create_resource_service(db: AsyncSession, resource_in: ResourceCreate) -> ResourceResponse:
    facility = await crud.get_facility_by_id(db, resource_in.facility_id)
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found."
        )
    new_resource = await crud.create_resource(db, resource_in)
    return ResourceResponse.model_validate(new_resource)

async def get_resource_by_id_service(db: AsyncSession, resource_id: UUID) -> ResourceResponse:
    resource = await crud.get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found."
        )
    return ResourceResponse.model_validate(resource)

async def get_resources_by_facility_id_service(db: AsyncSession, facility_id: UUID, pagination: PaginationParams) -> list[ResourceResponse]:
    offset = (pagination.page - 1) * pagination.page_size
    limit = pagination.page_size
    facility = await crud.get_facility_by_id(db, facility_id)
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found."
        )
    resources = await crud.get_resources_by_facility_id(db, facility_id, limit=limit, offset=offset)
    copy_resources = await crud.get_resources_by_facility_id(db, facility_id, limit=limit, offset=offset)
    for resource in copy_resources:
        print(resource.facility_id)
    return [ResourceResponse.model_validate(resource) for resource in resources]

async def delete_resource_service(db: AsyncSession, resource_id: UUID):
    resource = await crud.get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found."
        )
    await crud.delete_resource(db, resource)


async def update_resource_service(db: AsyncSession, resource_id: UUID, resource_in: ResourceUpdate) -> ResourceResponse:
    resource = await crud.get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found."
        )
    if resource_in.facility_id:
        facility = await crud.get_facility_by_id(db, resource_in.facility_id)
        if not facility:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Facility not found."
            )
    updated_resource = await crud.update_resource(db, resource, resource_in)
    return ResourceResponse.model_validate(updated_resource)


async def get_all_resources_service(db: AsyncSession, pagination: PaginationParams) -> list[ResourceResponse]:
    offset = (pagination.page - 1) * pagination.page_size
    limit = pagination.page_size
    resources = await crud.get_all_resources(db, limit=limit, offset=offset)
    return [ResourceResponse.model_validate(resource) for resource in resources]


async def create_booking_service(db: AsyncSession, booking_in: BookingCreate, user_id: UUID, facility_id: UUID) -> BookingResponse:
    check_resource_facility = await crud.get_resource_by_id(db, booking_in.resource_id)
    if not check_resource_facility or check_resource_facility.facility_id != facility_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found in the specified facility."
        )
    resource = await crud.get_resource_by_id(db, booking_in.resource_id)
    check_conflict = await crud.check_booking_conflict(db, booking_in.resource_id, booking_in.start_time, booking_in.end_time)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found."
        )
    if check_conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking conflict: The resource is already booked for the specified time range."
        )
    total_price = calculate_total_price(booking_in.start_time, booking_in.end_time, resource.price_per_hour)
    new_booking = await crud.create_booking(db, booking_in, user_id, total_price)
    return BookingResponse.model_validate(new_booking)

async def update_booking_service(db: AsyncSession, booking_id: UUID, booking_in: BookingUpdate) -> BookingResponse:
    booking = await crud.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found."
        )
    resource = await crud.get_resource_by_id(db, booking.resource_id)
    if booking_in.resource_id:
        resource = await crud.get_resource_by_id(db, booking_in.resource_id)
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found."
            )
    start_time = booking_in.start_time if booking_in.start_time else booking.start_time
    end_time = booking_in.end_time if booking_in.end_time else booking.end_time
    check_conflict = await crud.check_booking_conflict(db, booking_in.resource_id or booking.resource_id, start_time, end_time, exclude_booking_id=booking_id)
    if check_conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking conflict: The resource is already booked for the specified time range."
        )
    total_price = calculate_total_price(start_time, end_time, resource.price_per_hour)
    updated_booking = await crud.update_booking(db, booking, booking_in)
    updated_booking.total_price = total_price
    await db.commit()
    await db.refresh(updated_booking)
    return BookingResponse.model_validate(updated_booking)

async def get_booking_by_id_service(db: AsyncSession, booking_id: UUID, current_user: UserResponse) -> BookingResponse:
    booking = await crud.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found."
        )
    if booking.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this booking."
        )
    return BookingResponse.model_validate(booking)

async def get_bookings_by_user_id_service(db: AsyncSession, user_id: UUID, pagination: PaginationParams) -> list[BookingResponse]:
    offset = (pagination.page - 1) * pagination.page_size
    limit = pagination.page_size
    bookings = await crud.get_bookings_by_user_id(db, user_id, limit=limit, offset=offset)
    return [BookingResponse.model_validate(booking) for booking in bookings]


async def get_bookings_by_resource_id_service(db: AsyncSession, resource_id: UUID, pagination: PaginationParams) -> list[BookingResponse]:
    offset = (pagination.page - 1) * pagination.page_size
    limit = pagination.page_size
    bookings = await crud.get_bookings_by_resource_id(db, resource_id, limit=limit, offset=offset)
    return [BookingResponse.model_validate(booking) for booking in bookings]

async def get_bookings_by_facility_id_service(db: AsyncSession, facility_id: UUID, pagination: PaginationParams) -> list[BookingResponse]:
    offset = (pagination.page - 1) * pagination.page_size
    limit = pagination.page_size
    bookings = await crud.get_bookings_by_facility_id(db, facility_id, limit=limit, offset=offset)
    return [BookingResponse.model_validate(booking) for booking in bookings]


async def delete_booking_service(db: AsyncSession, booking_id: UUID):
    booking = await crud.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found."
        )
    await crud.delete_booking(db, booking)

async def get_all_bookings_service(db: AsyncSession, pagination: PaginationParams) -> list[BookingResponse]:
    offset = (pagination.page - 1) * pagination.page_size
    limit = pagination.page_size
    bookings = await crud.get_all_bookings(db, limit=limit, offset=offset)
    return [BookingResponse.model_validate(booking) for booking in bookings]

