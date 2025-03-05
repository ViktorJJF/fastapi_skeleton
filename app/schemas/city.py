from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CityBase(BaseModel):
    """
    Base schema for city data.
    """
    name: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None


class CityCreate(CityBase):
    """
    Schema for creating a new city.
    """
    name: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)


class CityUpdate(CityBase):
    """
    Schema for updating a city.
    """
    pass


class CityInDBBase(CityBase):
    """
    Base schema for city in database.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class City(CityInDBBase):
    """
    Schema for city response.
    """
    pass 