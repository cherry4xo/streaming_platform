import uuid
from typing import Optional
from datetime import date

from pydantic import BaseModel, validator, UUID4, EmailStr


class BaseProperties(BaseModel):
    @validator("uuid", pre=True, always=True, check_fields=False)
    def default_hashed_id(cls, v):
        return v or uuid.uuid4()


class BaseUser(BaseProperties):
    uuid: Optional[UUID4] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    registration_date: Optional[date] = None
    is_admin: Optional[bool] = None


class UserCreate(BaseProperties):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseUser):
    uuid: UUID4
    username: str
    email: EmailStr
    registration_date: date
    is_admin: bool