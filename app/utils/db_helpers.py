from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Generic
from fastapi import Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, update, delete as sqlalchemy_delete
from sqlalchemy.inspection import inspect
from sqlalchemy.sql import sqltypes
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

from app.utils.pagination import paginate, PaginatedResponse

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


def build_sort(sort: str, order: str) -> Dict[str, Any]:
    """
    Build sort dictionary for query.
    """
    return {sort: order}


async def list_init_options(request: Request) -> Dict[str, Any]:
    """
    Initialize options for listing items.
    """
    query_params = dict(request.query_params)
    order = query_params.get("order", "asc")
    sort = query_params.get("sort", "created_at")
    sort_by = build_sort(sort, order)
    page = int(query_params.get("page", "1"))
    limit = int(query_params.get("limit", "10"))

    return {
        "order": order,
        "sort": sort_by,
        "page": page,
        "limit": limit,
    }


async def check_query_string(
    query_params: Union[Dict[str, Any], "PaginationParams"], model: Type[ModelType]
) -> Dict[str, Any]:
    """
    Process query parameters for filtering, converting types based on the model.
    Can accept either a dictionary of query parameters or a PaginationParams object.
    """
    queries = {}
    model_mapper = inspect(model)

    # Check if input is a PaginationParams object
    if hasattr(query_params, "model_dump"):
        # Convert PaginationParams to dictionary
        pagination_dict = query_params.model_dump(exclude_unset=True)

        # Process pagination parameters
        queries["page"] = pagination_dict.get("page", 1)
        queries["size"] = pagination_dict.get("size", 10)
        queries["sort"] = pagination_dict.get("sort_by") or "created_at"
        queries["order"] = pagination_dict.get("sort_order") or "asc"

        # Add search parameter if provided
        if pagination_dict.get("search"):
            queries["filter"] = pagination_dict.get("search")
            queries["fields"] = "name,description"  # Fields to search in
    else:
        # Process as dictionary (for backwards compatibility)
        filter_value = query_params.get("filter")
        fields = query_params.get("fields")

        # Process pagination parameters
        try:
            page = int(query_params.get("page", "1"))
        except ValueError:
            page = 1

        try:
            size = int(query_params.get("size", "10"))
        except ValueError:
            size = 10

        # Add processed pagination parameters
        queries["page"] = page
        queries["size"] = size

        # Copy other query params
        for key, value in query_params.items():
            if key in ["filter", "fields", "page", "size", "limit"]:
                continue  # Skip special keys already handled

            if key in ["order", "sort"]:
                queries[key] = value  # Keep sort/order as strings
                continue

            # Process other parameters
            queries[key] = value

        # Setup filter parameters
        if filter_value and fields:
            queries["filter"] = filter_value
            queries["fields"] = fields

    # Process query parameters for type conversion based on model columns
    processed_queries = {}
    for key, value in queries.items():
        # Skip special pagination keys
        if key in ["filter", "fields", "filter_conditions"]:
            processed_queries[key] = value
            continue

        # For pagination-specific parameters, just copy them
        if key in ["page", "size", "sort", "order"]:
            processed_queries[key] = value
            continue

        # Check if the key is a column in the model
        if key in model_mapper.columns:
            column = model_mapper.columns[key]
            target_type = column.type.python_type
            try:
                # Attempt conversion
                if target_type is bool:
                    # Handle boolean conversion explicitly (e.g., 'true', 'false', '1', '0')
                    if isinstance(value, str) and value.lower() in ["true", "1"]:
                        converted_value = True
                    elif isinstance(value, str) and value.lower() in ["false", "0"]:
                        converted_value = False
                    elif isinstance(value, (bool, int)):
                        converted_value = bool(value)
                    else:
                        raise ValueError(f"Invalid boolean value for {key}: {value}")
                elif target_type is datetime:
                    # Add more robust datetime parsing if needed (e.g., different formats)
                    converted_value = datetime.fromisoformat(value)
                else:
                    # General conversion for int, float, etc.
                    converted_value = target_type(value)

                processed_queries[key] = converted_value
            except (ValueError, TypeError) as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid value for parameter '{key}'. Expected type {target_type.__name__}, but received '{value}'. Error: {e}",
                )
        else:
            # If not a model column, keep it as is (string)
            processed_queries[key] = value

    # Process filter conditions
    try:
        if processed_queries.get("filter") and processed_queries.get("fields"):
            field_list = processed_queries["fields"].split(",")
            filter_conditions = []

            for field in field_list:
                # Ensure the filter field exists in the model before adding
                if field in model_mapper.columns:
                    # We don't type-convert the filter_value itself here, as 'ilike' expects a string pattern
                    filter_conditions.append(
                        {field: {"ilike": f"%{processed_queries['filter']}%"}}
                    )
                # else: Optionally warn or error if filter field doesn't exist

            # Return combined filter conditions with other queries
            if filter_conditions:
                processed_queries["filter_conditions"] = filter_conditions

        return processed_queries  # Return processed queries
    except Exception as e:
        # Catch potential errors during filter processing specifically
        raise HTTPException(
            status_code=422, detail=f"Error processing filter parameters: {str(e)}"
        )


async def get_all_items(db: AsyncSession, model: Type[ModelType]) -> List[ModelType]:
    """
    Get all items from a model.
    """
    query = select(model).order_by(model.id)
    result = await db.execute(query)
    return result.scalars().all()


async def get_items(
    db: AsyncSession,
    model: Type[ModelType],
    request: Request,
    processed_query: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Get items with pagination, sorting, and filtering.

    Parameters:
    -----------
    db: AsyncSession
        The database session.
    model: Type[ModelType]
        The SQLAlchemy model class to query.
    request: Request
        The FastAPI request object containing query parameters.
    processed_query: Dict[str, Any]
        Processed query parameters with proper type conversion.

    Query Parameters:
    ----------------
    page: int
        Page number (default: 1)
    size/limit: int
        Number of items per page (default: 10)
    sort: str
        Field name to sort by (default: "created_at")
    order: str
        Sort order, "asc" or "desc" (default: "asc")
    filter: str
        Text to search across specified fields
    fields: str
        Comma-separated list of fields to apply the filter on

    Additional model-specific filters can be provided as query parameters.
    Any parameter that matches a column name in the model will be used for filtering.

    Returns:
    --------
    Dict[str, Any]
        A response containing items and pagination metadata in the format:
        {
            "ok": true,
            "totalDocs": total number of items,
            "limit": items per page,
            "totalPages": total number of pages,
            "page": current page number,
            "pagingCounter": current page number,
            "hasPrevPage": boolean indicating if previous page exists,
            "hasNextPage": boolean indicating if next page exists,
            "prevPage": previous page number or null,
            "nextPage": next page number or null,
            "payload": list of items
        }
    """

    # Extract pagination options after processing
    page = processed_query.pop("page", 1)
    limit = processed_query.pop("size", 10)
    order = processed_query.pop("order", "asc")  # Default order
    sort_field_name = processed_query.pop(
        "sort", "id"
    )  # Default sort field, assuming 'id' exists

    # Build sort dictionary
    sort_by = build_sort(sort_field_name, order)

    # Build base query
    query = select(model)

    # Apply filters (ilike from filter_conditions)
    filter_conditions = processed_query.pop("filter_conditions", None)
    if filter_conditions:
        filter_clauses = []
        for condition in filter_conditions:
            for field, value in condition.items():
                column = getattr(model, field)
                if "ilike" in value:
                    filter_clauses.append(column.ilike(value["ilike"]))

        if filter_clauses:
            query = query.where(or_(*filter_clauses))

    # Apply other filters (now with correct types from processed_query)
    for field, value in processed_query.items():
        if hasattr(model, field):
            # Use the pre-validated and type-converted value directly
            query = query.where(getattr(model, field) == value)
        # else: Decide how to handle query params that are not model fields

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.execute(count_query)
    total_count = total.scalar() or 0

    # Apply pagination
    query = query.offset((page - 1) * limit).limit(limit)

    # Apply sorting
    # sort_field = options["sort"] # Use sort_by dictionary
    for field, direction in sort_by.items():
        if hasattr(model, field):
            column = getattr(model, field)
            if direction.lower() == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        # else: Optionally raise error if sort field is invalid

    # Execute query
    result = await db.execute(query)
    items = result.scalars().all()

    # Convert items to dictionaries
    items_dict = [
        (
            item.to_dict()
            if hasattr(item, "to_dict")
            else dict(item) if hasattr(item, "keys") else vars(item)
        )
        for item in items
    ]

    # Calculate total pages
    total_pages = (total_count + limit - 1) // limit if limit > 0 else 0

    # Calculate previous and next pages
    has_prev_page = page > 1
    has_next_page = page < total_pages
    prev_page = page - 1 if has_prev_page else None
    next_page = page + 1 if has_next_page else None

    # Return formatted response
    return {
        "ok": True,
        "totalDocs": total_count,
        "limit": limit,
        "totalPages": total_pages,
        "page": page,
        "pagingCounter": page,
        "hasPrevPage": has_prev_page,
        "hasNextPage": has_next_page,
        "prevPage": prev_page,
        "nextPage": next_page,
        "payload": items_dict,
    }


async def get_item(
    db: AsyncSession, model: Type[ModelType], id: int
) -> Optional[ModelType]:
    """
    Get a single item by ID.
    """
    query = select(model).where(model.id == id)
    result = await db.execute(query)
    item = result.scalars().first()

    return item


async def filter_items(
    db: AsyncSession, model: Type[ModelType], filters: Dict[str, Any]
) -> List[ModelType]:
    """
    Filter items by fields.
    """
    query = select(model)

    for field, value in filters.items():
        if hasattr(model, field):
            query = query.where(getattr(model, field) == value)

    result = await db.execute(query)
    return result.scalars().all()


async def create_item(
    db: AsyncSession, model: Type[ModelType], data: Dict[str, Any]
) -> ModelType:
    """
    Create a new item.
    """
    try:
        db_item = model(**data)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=422, detail=f"Error creating item: {str(e)}")


async def update_item(
    db: AsyncSession,
    model: Type[ModelType],
    id: int,
    data: Union[Dict[str, Any], BaseModel],
) -> Optional[ModelType]:
    """
    Update an existing item.
    """
    try:
        # Convert Pydantic models to dict if needed
        if isinstance(data, BaseModel):
            data_dict = data.dict(exclude_unset=True)
        else:
            data_dict = data

        stmt = update(model).where(model.id == id).values(**data_dict).returning(model)
        result = await db.execute(stmt)
        await db.commit()

        # Get the updated item
        updated_item = result.scalars().first()

        if not updated_item:
            return None

        return updated_item.to_dict()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=422, detail=f"Error updating item: {str(e)}")


async def delete_item(
    db: AsyncSession, model: Type[ModelType], id: int
) -> Optional[ModelType]:
    """
    Delete an item.
    """
    item = await get_item(db, model, id)

    if not item:
        return None

    try:
        await db.delete(item)
        await db.commit()
        return item
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=422, detail=f"Error deleting item: {str(e)}")


async def delete_items_by_ids(
    db: AsyncSession, model: Type[ModelType], ids: List[int]
) -> int:
    """
    Delete multiple items by their IDs.
    Returns the number of rows deleted.
    """
    if not ids:
        return 0  # No IDs provided, nothing to delete

    try:
        stmt = sqlalchemy_delete(model).where(model.id.in_(ids))
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount
    except Exception as e:
        await db.rollback()
        # Consider logging the error here
        raise HTTPException(
            status_code=500, detail=f"Error performing bulk delete: {str(e)}"
        )
