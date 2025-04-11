from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

# Base User Schema
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    name: Optional[str] = Field(None, description="User's full name")
    role: Optional[str] = Field("USER", description="User role (e.g., USER, ADMIN)")
    verified: Optional[bool] = Field(False, description="Whether the user email is verified")

# Schema for creating a new user
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="User's password (min  characters)")

# Schema for updating a user
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    verified: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6, description="New password (optional, min 6 characters)")
    login_attempts: Optional[int] = None
    block_expires: Optional[datetime] = None

# Schema for representing a user in responses (excluding sensitive info)
class User(UserBase):
    id: UUID = Field(..., description="Unique identifier for the user")
    created_at: datetime = Field(..., description="Timestamp when the user was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the user was last updated")
    login_attempts: Optional[int] = Field(0, description="Number of failed login attempts")
    block_expires: Optional[datetime] = Field(None, description="Timestamp until the user is blocked")

    class Config:
        from_attributes = True # Allow creating from ORM objects

class UserInDBBase(UserBase):
    id: UUID
    hashed_password: str
    verification_token: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    login_attempts: int = 0
    block_expires: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema for user data stored in the database
class UserInDB(UserInDBBase):
    pass

# Schema for user data included in JWT token payload
class UserInToken(BaseModel):
    id: UUID
    role: str
    email: EmailStr

class UserDeleteManyInput(BaseModel):
    ids: list[str] = Field(..., description="List of User IDs to delete") 