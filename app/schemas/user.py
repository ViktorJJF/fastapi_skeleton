from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Base schema for user data.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserUpdate(UserBase):
    """
    Schema for updating a user.
    """
    password: Optional[str] = Field(None, min_length=8)


class UserInDBBase(UserBase):
    """
    Base schema for user in database.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class User(UserInDBBase):
    """
    Schema for user response.
    """
    pass


class UserInDB(UserInDBBase):
    """
    Schema for user in database with hashed password.
    """
    hashed_password: str 