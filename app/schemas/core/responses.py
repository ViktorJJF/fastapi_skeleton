from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field

from app.schemas.core.paginations import PaginatedResponse

# Generic type for payload
T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """Base model for all API responses."""
    ok: bool = Field(..., description="Indicates if the request was successful")
    payload: T = Field(..., description="Response payload data")


class SingleItemResponse(ApiResponse[Any]):
    """API response containing a single item."""
    payload: Any = Field(..., description="Single item payload")


class ListResponse(ApiResponse[List[Any]]):
    """API response containing a list of items."""
    payload: List[Any] = Field(..., description="List of items")


class PaginatedApiResponse(ApiResponse[PaginatedResponse]):
    """API response containing paginated data."""
    payload: PaginatedResponse = Field(..., description="Paginated data")


class DeleteResponse(ApiResponse[Dict[str, Any]]):
    """API response for deletion operations."""
    payload: Dict[str, Any] = Field(..., description="Deletion result information")


class DeleteManyResponse(ApiResponse[Dict[str, Any]]):
    """API response for batch deletion operations."""
    payload: Dict[str, Any] = Field(
        ..., 
        description="Batch deletion results",
        example={
            "deleted_count": 5,
            "requested_ids": [1, 2, 3, 4, 5],
            "valid_ids_processed": [1, 2, 3, 4, 5],
            "invalid_ids_found": []
        }
    ) 