from pydantic import BaseModel, Field
from typing import List, Any
from datetime import datetime


class AssistantBase(BaseModel):
    """Base model for assistant attributes."""
    name: str | None = Field(None, description="The name of the assistant")
    description: str | None = Field(None, description="A description of the assistant's purpose and capabilities")


class AssistantCreate(AssistantBase):
    """Model used when creating an assistant."""
    name: str = Field(..., min_length=1, max_length=100, description="The name of the assistant")


class AssistantUpdate(AssistantBase):
    """Model used when updating an assistant."""
    pass


class AssistantInDBBase(AssistantBase):
    """Base model for assistant in database."""
    id: int = Field(..., description="The unique identifier of the assistant")
    created_at: datetime = Field(..., description="Timestamp when the assistant was created")
    updated_at: datetime = Field(..., description="Timestamp when the assistant was last updated")

    model_config = {
        "from_attributes": True
    }


class Assistant(AssistantInDBBase):
    """Model used when reading an assistant."""
    pass


class AssistantDeleteManyInput(BaseModel):
    """Input model for batch deletion of assistants."""
    ids: List[str] = Field(..., description="A list of assistant IDs to delete") 