from pydantic import BaseModel, Field
from typing import List, Generic, TypeVar, Optional, Any, Dict

T = TypeVar('T')


class PaginationParams(BaseModel):
    """
    Common query parameters for pagination.
    """
    page: int = Field(1, ge=1, description="Page number (starts at 1)")
    limit: int = Field(10, ge=1, le=100, description="Number of items per page")
    

class SortingParams(BaseModel):
    """
    Common query parameters for sorting.
    """
    sort: str = Field("created_at", description="Field name to sort by")
    order: str = Field("asc", description="Sort order (asc or desc)")


class FilteringParams(BaseModel):
    """
    Common query parameters for filtering.
    """
    filter: Optional[str] = Field(None, description="Text to search across specified fields")
    fields: Optional[str] = Field(None, description="Comma-separated list of fields to search")


class PaginatedListParams(PaginationParams, SortingParams, FilteringParams):
    """
    Combined query parameters for paginated, sorted, and filtered lists.
    """
    pass


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response model.
    """
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [{"id": 1, "name": "Example Item"}],
                    "total": 50,
                    "page": 1,
                    "size": 10,
                    "pages": 5
                }
            ]
        }
    } 