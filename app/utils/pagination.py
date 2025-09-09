from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from fastapi import Query

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response.
    """

    items: List[T]
    total: int
    page: int
    size: int
    pages: int


def paginate(items: List[T], total: int, page: int, size: int) -> PaginatedResponse[T]:
    """
    Create a paginated response.
    """
    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedResponse(
        items=items, total=total, page=page, size=size, pages=pages
    )


def pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
) -> tuple[int, int]:
    """
    Common pagination parameters.
    """
    return page, size
