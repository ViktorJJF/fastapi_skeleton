
from pydantic import BaseModel, Field
from typing import List, Any

class PaginationParams(BaseModel):
    """Parameters for pagination."""
    page: int = Field(1, ge=1, description="Page number (starts at 1)")
    size: int = Field(10, ge=1, le=100, description="Number of items per page (1-100)")
    sort_by: str | None = Field(None, description="Field to sort by")
    sort_order: str | None = Field("asc", description="Sort order (asc or desc)")
    search: str | None = Field(None, description="Search term to filter assistants by name or description")


class PaginatedResponse(BaseModel):
    """Base model for paginated responses."""
    items: List[Any] = Field(..., description="List of items on the current page")
    total: int = Field(..., description="Total number of items across all pages")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")

    model_config = {
        "arbitrary_types_allowed": True
    }