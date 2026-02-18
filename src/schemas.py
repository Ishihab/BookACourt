from pydantic import BaseModel, EmailStr, field_validator, computed_field
from uuid import UUID
from datetime import datetime, time 
from fastapi import UploadFile


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 10

class ORMBase(BaseModel):
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }



class UserBase(ORMBase):
    email: EmailStr
    full_name: str 
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(ORMBase):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None

class UserResponse(UserBase):
    id: UUID
    profile_image_key: str | None = None



class UserSignup(ORMBase):
    full_name: str
    email: EmailStr
    password: str

    @field_validator('email', mode='before')
    @classmethod
    def check_at_symbol(cls, value: str) -> str:
        # Check if the input is a string and contains '@'
        if isinstance(value, str) and '@' not in value:
            # You can either raise a custom error or try to "fix" it
            raise ValueError("Email must contain an '@' character")
        return value

class UserLogin(ORMBase):
    email: EmailStr
    password: str
    @field_validator('email', mode='before')
    @classmethod
    def check_at_symbol(cls, value: str) -> str:
        # Check if the input is a string and contains '@'
        if isinstance(value, str) and '@' not in value:
            # You can either raise a custom error or try to "fix" it
            raise ValueError("Email must contain an '@' character")
        return value

class UserUpdateMe(ORMBase):
    full_name: str | None = None
    email: EmailStr | None = None

class UserUpdatePic(ORMBase):
    img_url: UploadFile

class UserProfileResponse(UserBase):
    id: UUID
    email: EmailStr
    full_name: str | None = None
    profile_image_key: str | None = None
    phone_number: str | None = None
    is_verified: bool = False
    created_at: datetime | None = None

class ChangePassword(ORMBase):
    old_password: str
    new_password: str

class ResetPassword(ORMBase):
    token: str
    new_password: str

class Token(ORMBase):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(ORMBase):
    user_id: str | None = None


class FacilityBase(ORMBase):
    name: str
    state: str
    city: str
    address: str
    phone_number: str | None = None
    email: EmailStr | None = None
    open_at: time | None = None
    close_at: time | None = None

    @field_validator("email", "open_at", "close_at", mode="before")
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v


class FacilityCreate(FacilityBase):
    pass

class FacilityUpdate(ORMBase):
    name: str | None = None
    state: str | None = None
    city: str | None = None
    address: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    open_at: time | None = None
    close_at: time | None = None

    @field_validator("email", "open_at", "close_at", mode="before")
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

class FacilityResponse(FacilityBase):
    id: UUID


class FacilityListResponse(ORMBase):
    facilities: list[FacilityResponse]

class FacilityImgUpload(ORMBase):
    img_content: UploadFile

    @field_validator("img_content", mode="before")
    def validate_image(cls, v):
        if not v.content_type.startswith("image/"):
            raise ValueError("Uploaded file must be an image")
        return v
    
    


    


class ResourceBase(ORMBase):
    facility_id: UUID
    name: str
    price_per_hour: float
    description: str | None = None

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(ORMBase):
    facility_id: UUID | None = None
    name: str | None = None
    price_per_hour: float | None = None
    description: str | None = None

class ResourceResponse(ResourceBase):
    id: UUID


class BookingBase(ORMBase):
    resource_id: UUID
    start_time: datetime
    end_time: datetime


class BookingCreate(BookingBase):
    pass 

class BookingResponse(BookingBase):
    id: UUID
    total_price: float
    user_id: UUID

class BookingUpdate(ORMBase):
    resource_id: UUID | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None




























# class FacilityBase(ORMBase):
#     name: str
#     state: str
#     city: str
#     address: str
#     open_at: time | None = None
#     close_at: time | None = None
#     amenities: dict | None = None

# class FacilityCreate(FacilityBase):
#     pass

# class FacilityUpdate(ORMBase):
#     name: str | None = None
#     state: str | None = None
#     city: str | None = None
#     address: str | None = None
#     open_at: str | None = None
#     close_at: str | None = None
#     amenities: dict | None = None

# class FacilityResponse(FacilityBase):
#     id: UUID

