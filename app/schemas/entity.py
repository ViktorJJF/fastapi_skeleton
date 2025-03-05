from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EntityBase(BaseModel):
    """
    Base schema for entity data.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    assistant_id: Optional[int] = None


class EntityCreate(EntityBase):
    """
    Schema for creating a new entity.
    """
    name: str = Field(..., min_length=1, max_length=100)
    assistant_id: int


class EntityUpdate(EntityBase):
    """
    Schema for updating an entity.
    """
    pass


class EntityInDBBase(EntityBase):
    """
    Base schema for entity in database.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Entity(EntityInDBBase):
    """
    Schema for entity response.
    """
    pass 