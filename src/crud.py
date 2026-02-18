from src.models import Users, Resources, Bookings, Facilities
from src.schemas import (
    UserSignup, 
    UserUpdate, 
    UserUpdateMe, 
    FacilityCreate, 
    FacilityUpdate, 
    FacilityResponse,
    ResourceCreate, 
    ResourceUpdate, 
    ResourceResponse, 
    BookingCreate, 
    BookingUpdate, 
    BookingResponse)
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy.future import select
from src.core.security import hash_password, verify_password
from sqlalchemy import or_, and_, Index, UniqueConstraint, CheckConstraint
from datetime import datetime, timezone
from src.utils import get_pagination




async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Users:
    return await db.get(Users, user_id)

async def get_user_by_email(db: AsyncSession, email: str) -> Users:
    result = await db.execute(select(Users).where(Users.email == email))
    user = result.scalars().first()
    return user

async def create_user(db: AsyncSession, user_in: UserSignup) -> Users:
    profile_img_key = f'https://ui-avatars.com/api/?background=random&name={user_in.full_name}&size=128&rounded=true'
    new_user = Users(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),  
        full_name=user_in.full_name,
        profile_image_key=profile_img_key
        
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user(db: AsyncSession, user: Users, user_in: UserUpdate) -> Users:
    user_data = user_in.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = hash_password(user_data.pop("password"))
    for field, value in user_data.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_me(db: AsyncSession, user: Users, user_in: UserUpdateMe) -> Users:
    user_data = user_in.model_dump(exclude_unset=True)
    for field, value in user_data.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user

async def get_all_users(db: AsyncSession, limit: int, offset: int) -> list[Users]:
    result = await db.execute(select(Users).offset(offset).limit(limit))
    return result.scalars().all()

DUMMY_HASH = "$argon2id$v=19$m=16,t=2,p=1$WUZMTm9ydTVmcDRDbThCSg$8tIAZgUeWI+sbcOvj2f9Sw"


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Users:
    user = await get_user_by_email(db, email)
    if not user:
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_facility_by_name_city(db: AsyncSession, name: str, city: str) -> Facilities:
    result = await db.execute(select(Facilities).where(Facilities.name == name, Facilities.city == city))
    return result.scalars().first()



async def create_facility(db: AsyncSession, facility_in: FacilityCreate):
    new_facility = Facilities(
        name=facility_in.name,
        city=facility_in.city,
        state=facility_in.state,
        address=facility_in.address,
        open_at=facility_in.open_at,
        close_at=facility_in.close_at,
    )
    db.add(new_facility)
    await db.commit()
    await db.refresh(new_facility)
    return new_facility

async def get_facility_by_id(db: AsyncSession, facility_id: UUID) -> Facilities:
    return await db.get(Facilities, facility_id)

async def get_all_facilities(db: AsyncSession, limit: int, offset: int) -> list[Facilities]:
    result = await db.execute(select(Facilities).offset(offset).limit(limit))
    return result.scalars().all()

async def delete_facility(db: AsyncSession, facility: Facilities):
    await db.delete(facility)
    await db.commit()

async def update_facility(db: AsyncSession, facility: Facilities, facility_in: FacilityUpdate) -> Facilities:
    facility_data = facility_in.model_dump(exclude_unset=True)
    for field, value in facility_data.items():
        setattr(facility, field, value)
    await db.commit()
    await db.refresh(facility)
    return facility

async def create_resource(db: AsyncSession, resource_in: ResourceCreate):
    new_resource = Resources(
        facility_id=resource_in.facility_id,
        name=resource_in.name,
        description=resource_in.description,
        price_per_hour=resource_in.price_per_hour
    )
    db.add(new_resource)
    await db.commit()
    await db.refresh(new_resource)
    return new_resource

async def get_resource_by_id(db: AsyncSession, resource_id: UUID) -> Resources:
    return await db.get(Resources, resource_id)

async def get_resources_by_facility_id(db: AsyncSession, facility_id: UUID, limit: int, offset: int) -> list[Resources]:
    result = await db.execute(select(Resources).where(Resources.facility_id == facility_id).offset(offset).limit(limit))
    return result.scalars().all()

async def delete_resource(db: AsyncSession, resource: Resources):
    await db.delete(resource)
    await db.commit()


async def update_resource(db: AsyncSession, resource: Resources, resource_in: ResourceUpdate) -> Resources:
    resource_data = resource_in.model_dump(exclude_unset=True)
    for field, value in resource_data.items():
        setattr(resource, field, value)
    await db.commit()
    await db.refresh(resource)
    return resource


async def get_all_resources(db: AsyncSession, limit: int, offset: int) -> list[Resources]:
    result = await db.execute(select(Resources).offset(offset).limit(limit))
    return result.scalars().all()


async def create_booking(db: AsyncSession, booking_in: BookingCreate, user_id: UUID, total_price: float) -> Bookings:
    new_booking = Bookings(
        resource_id=booking_in.resource_id,
        user_id=user_id,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time,
        total_price=total_price
    )
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)
    return new_booking

async def update_booking(db: AsyncSession, booking: Bookings, booking_in: BookingUpdate) -> Bookings:
    booking_data = booking_in.model_dump(exclude_unset=True)
    for field, value in booking_data.items():
        setattr(booking, field, value)
    await db.commit()
    await db.refresh(booking)
    return booking




async def check_booking_conflict(db: AsyncSession, resource_id: UUID, start_time: datetime, end_time: datetime, exclude_booking_id: UUID | None = None) -> bool:
    query = select(Bookings).where(
        Bookings.resource_id == resource_id,
        Bookings.start_time < end_time,
        Bookings.end_time > start_time
    )
    if exclude_booking_id:
        query = query.where(Bookings.id != exclude_booking_id)
    result = await db.execute(query)
    return result.scalars().first() is not None

async def get_booking_by_id(db: AsyncSession, booking_id: UUID) -> Bookings:
    return await db.get(Bookings, booking_id)

async def get_bookings_by_user_id(db: AsyncSession, user_id: UUID, limit: int, offset: int) -> list[Bookings]:
    result = await db.execute(select(Bookings).where(Bookings.user_id == user_id).offset(offset).limit(limit))
    return result.scalars().all()

async def get_bookings_by_resource_id(db: AsyncSession, resource_id: UUID, limit: int, offset: int) -> list[Bookings]:
    result = await db.execute(select(Bookings).where(Bookings.resource_id == resource_id).offset(offset).limit(limit))
    return result.scalars().all()


async def delete_booking(db: AsyncSession, booking: Bookings):
    await db.delete(booking)
    await db.commit()


async def get_all_bookings(db: AsyncSession, limit: int, offset: int) -> list[Bookings]:
    result = await db.execute(select(Bookings).offset(offset).limit(limit))
    return result.scalars().all()


async def get_bookings_by_facility_id(db: AsyncSession, facility_id: UUID, limit: int, offset: int) -> list[Bookings]:
    result = await db.execute(
        select(Bookings).join(Resources).where(Resources.facility_id == facility_id).offset(offset).limit(limit)
    )
    return result.scalars().all()





