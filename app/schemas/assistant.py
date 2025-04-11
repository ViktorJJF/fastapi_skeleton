from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AssistantBase(BaseModel):
    """
    Base schema for assistant data.
    """
    name: Optional[str] = None
    description: Optional[str] = None


class AssistantCreate(AssistantBase):
    """
    Schema for creating a new assistant.
    """
    name: str = Field(..., min_length=1, max_length=100)


class AssistantUpdate(AssistantBase):
    """
    Schema for updating an assistant.
    """
    pass


class AssistantInDBBase(AssistantBase):
    """
    Base schema for assistant in database.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class Assistant(AssistantInDBBase):
    """
    Schema for assistant response.
    """
    pass


class AssistantDeleteManyInput(BaseModel):
    """
    Schema for deleting multiple assistants by their IDs.
    """
    ids: List[str] = Field(..., description="A list of assistant IDs to delete.") 