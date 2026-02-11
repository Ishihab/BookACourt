from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime, time 

class ORMBase(BaseModel):
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class UserBase(ORMBase):
    email: EmailStr
    full_name: str | None = None
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



class UserSignup(ORMBase):
    email: EmailStr
    password: str

class UserUpdateMe(ORMBase):
    full_name: str | None = None
    email: EmailStr | None = None

class ChangePassword(ORMBase):
    old_password: str
    new_password: str

class ResetPassword(ORMBase):
    token: str
    new_password: str

class Token(ORMBase):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(ORMBase):
    user_id: str | None = None

class FacilityBase(ORMBase):
    name: str
    state: str
    city: str
    address: str
    open_at: time | None = None
    close_at: time | None = None
    amenities: dict | None = None

class FacilityCreate(FacilityBase):
    pass

class FacilityUpdate(ORMBase):
    name: str | None = None
    state: str | None = None
    city: str | None = None
    address: str | None = None
    open_at: str | None = None
    close_at: str | None = None
    amenities: dict | None = None

class FacilityResponse(FacilityBase):
    id: UUID

