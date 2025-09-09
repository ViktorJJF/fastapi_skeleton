from pydantic import BaseModel, Field
from typing import List, Any
from datetime import datetime

from app.schemas.core.responses import ApiResponse
from app.schemas.core.paginations import PaginatedResponse


class AssistantBase(BaseModel):
    """Base model for assistant attributes."""

    name: str | None = Field(None, description="The name of the assistant")
    description: str | None = Field(
        None, description="A description of the assistant's purpose and capabilities"
    )
    status: bool | None = Field(None, description="The status of the assistant")


class AssistantCreate(AssistantBase):
    """Model used when creating an assistant."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="The name of the assistant"
    )


class AssistantUpdate(AssistantBase):
    """Model used when updating an assistant."""

    pass


class AssistantInDBBase(AssistantBase):
    """Base model for assistant in database."""

    id: int = Field(..., description="The unique identifier of the assistant")
    created_at: datetime = Field(
        ..., description="Timestamp when the assistant was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the assistant was last updated"
    )

    model_config = {"from_attributes": True}


class Assistant(AssistantInDBBase):
    """Model used when reading an assistant."""

    pass


class AssistantDeleteManyInput(BaseModel):
    """Input model for batch deletion of assistants."""

    ids: List[str] = Field(..., description="A list of assistant IDs to delete")


# Response models for proper Swagger documentation
class AssistantResponse(ApiResponse[Assistant]):
    """API response containing a single assistant."""

    payload: Assistant = Field(..., description="Assistant data")


class AssistantListResponse(ApiResponse[List[Assistant]]):
    """API response containing a list of assistants."""

    payload: List[Assistant] = Field(..., description="List of assistants")


class AssistantPaginatedResponse(BaseModel):
    """Paginated response specifically for assistants."""

    ok: bool = Field(..., description="Indicates if the request was successful")
    payload: "AssistantPaginatedPayload" = Field(
        ..., description="Paginated assistant data"
    )


class AssistantPaginatedPayload(BaseModel):
    """Payload for paginated assistant responses."""

    payload: List[Assistant] = Field(
        ..., description="List of assistants on current page"
    )
    totalDocs: int = Field(
        ..., description="Total number of assistants across all pages"
    )
    limit: int = Field(..., description="Number of assistants per page")
    totalPages: int = Field(..., description="Total number of pages")
    page: int = Field(..., description="Current page number")
    pagingCounter: int = Field(..., description="The current page number")
    hasPrevPage: bool = Field(..., description="Whether there is a previous page")
    hasNextPage: bool = Field(..., description="Whether there is a next page")
    prevPage: int | None = Field(None, description="Previous page number if it exists")
    nextPage: int | None = Field(None, description="Next page number if it exists")
