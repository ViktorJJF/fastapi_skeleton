from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse

from app.models.Assistants import Assistant
from app.schemas.assistant import (
    AssistantCreate,
    AssistantUpdate,
    AssistantDeleteManyInput,
    Assistant as AssistantSchema,
)
from app.schemas.core.paginations import PaginationParams
from app.utils.db_helpers import (
    get_items,
    get_item,
    create_item,
    update_item,
    delete_item,
    check_query_string,
    delete_items_by_ids,
)
from app.utils.error_handling import handle_error, is_id_valid, build_error_object


async def list_paginated(
    request: Request, pagination: PaginationParams, db: AsyncSession
) -> JSONResponse:
    """
    List assistants with pagination.
    """
    try:
        processed_query = await check_query_string(pagination, Assistant)
        result = await get_items(db, Assistant, request, processed_query)

        # Convert payload items to Pydantic models with datetime serialization
        items_data = result["payload"]
        items = [
            AssistantSchema.model_validate(item).model_dump(mode="json")
            for item in items_data
        ]

        # Build proper paginated response structure
        response_data = {
            "ok": True,
            "payload": {
                "payload": items,
                "totalDocs": result["totalDocs"],
                "limit": result["limit"],
                "totalPages": result["totalPages"],
                "page": result["page"],
                "pagingCounter": result["pagingCounter"],
                "hasPrevPage": result["hasPrevPage"],
                "hasNextPage": result["hasNextPage"],
                "prevPage": result["prevPage"],
                "nextPage": result["nextPage"],
            },
        }

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_data,
        )
    except Exception as e:
        return await handle_error(request, e)


async def get_one(id: str, request: Request, db: AsyncSession) -> JSONResponse:
    """
    Get one assistant by ID.
    """
    try:
        valid_id = is_id_valid(id)
        item = await get_item(db, Assistant, valid_id)
        if not item:
            raise build_error_object(status.HTTP_404_NOT_FOUND, "Assistant not found")

        # Convert database model to Pydantic model
        assistant_schema = AssistantSchema.model_validate(item)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "payload": assistant_schema.model_dump(mode="json")},
        )
    except Exception as e:
        return await handle_error(request, e)


async def create(
    item: AssistantCreate, request: Request, db: AsyncSession
) -> JSONResponse:
    """
    Create a new item.
    """
    try:
        # Convert Pydantic model to dictionary for database creation
        item_data = item.model_dump(exclude_unset=True)
        created_item = await create_item(db, Assistant, item_data)
        # convert to valid dict
        created_item_dict = created_item.to_dict()
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"ok": True, "payload": created_item_dict},
        )
    except Exception as e:
        return await handle_error(request, e)


async def update(
    id: str, item: AssistantUpdate, request: Request, db: AsyncSession
) -> JSONResponse:
    """
    Update an item.
    """
    try:
        valid_id = is_id_valid(id)
        # Convert Pydantic model to dictionary for database update
        update_data = item.model_dump(exclude_unset=True)
        updated_item = await update_item(db, Assistant, valid_id, update_data)
        if not updated_item:
            raise build_error_object(status.HTTP_404_NOT_FOUND, "Assistant not found")

        # Convert database model to Pydantic model
        assistant_schema = AssistantSchema.model_validate(updated_item)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "payload": assistant_schema.model_dump(mode="json")},
        )
    except Exception as e:
        return await handle_error(request, e)


async def delete(id: str, request: Request, db: AsyncSession) -> JSONResponse:
    """
    Delete an item.
    """
    try:
        valid_id = is_id_valid(id)
        deleted = await delete_item(db, Assistant, valid_id)
        if not deleted:
            raise build_error_object(status.HTTP_404_NOT_FOUND, "Assistant not found")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "payload": {"id": valid_id, "deleted": True}},
        )
    except Exception as e:
        return await handle_error(request, e)


async def delete_many(
    request: Request, item: AssistantDeleteManyInput, db: AsyncSession
) -> JSONResponse:
    """
    Delete multiple items by their IDs.
    """
    try:
        valid_ids = []
        invalid_ids = []
        for assistant_id in item.ids:
            try:
                valid_id = is_id_valid(assistant_id)
                valid_ids.append(valid_id)
            except HTTPException:
                invalid_ids.append(assistant_id)

        if invalid_ids:
            raise build_error_object(
                status.HTTP_400_BAD_REQUEST,
                f"Invalid IDs provided: {', '.join(invalid_ids)}",
            )

        if not valid_ids:
            raise build_error_object(
                status.HTTP_400_BAD_REQUEST, "No valid IDs provided for deletion."
            )

        deleted_count = await delete_items_by_ids(db, Assistant, valid_ids)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "ok": True,
                "payload": {
                    "deleted_count": deleted_count,
                    "requested_ids": item.ids,
                    "valid_ids_processed": valid_ids,
                    "invalid_ids_found": invalid_ids,
                },
            },
        )
    except Exception as e:
        # Rollback might be redundant if the helper also rolls back, but good for safety
        await db.rollback()
        return await handle_error(request, e)
