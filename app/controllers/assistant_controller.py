from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse

# Remove direct import of sqlalchemy_delete if no longer needed elsewhere in the file
# from sqlalchemy import delete as sqlalchemy_delete

from app.models.assistant import Assistant
from app.schemas.assistant import (
    AssistantCreate,
    AssistantUpdate,
    Assistant as AssistantSchema,
    AssistantDeleteManyInput,
)
from app.schemas.core.paginations import PaginationParams
from app.utils.db_helpers import (
    get_all_items,
    get_items,
    get_item,
    create_item,
    update_item,
    delete_item,
    check_query_string,
    delete_items_by_ids,  # Import the new helper function
)
from app.utils.error_handling import handle_error, is_id_valid, build_error_object


async def create(
    item: AssistantCreate, request: Request, db: AsyncSession
) -> JSONResponse:
    """
    Create a new assistant.
    """
    try:
        # Create item
        item = await create_item(db, Assistant, item)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"ok": True, "payload": item.to_dict()},
        )
    except Exception as e:
        return await handle_error(request, e)


async def update(
    id: str, item: AssistantUpdate, request: Request, db: AsyncSession
) -> JSONResponse:
    """
    Update an assistant.
    """
    try:
        # Validate ID
        valid_id = is_id_valid(id)

        # Update item
        updated_item = await update_item(db, Assistant, valid_id, item)
        if not updated_item:
            raise build_error_object(status.HTTP_404_NOT_FOUND, "Assistant not found")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "payload": updated_item},
        )
    except Exception as e:
        return await handle_error(request, e)


async def delete(id: str, request: Request, db: AsyncSession) -> JSONResponse:
    """
    Delete an assistant.
    """
    try:
        # Validate ID
        valid_id = is_id_valid(id)

        # Delete item
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
    Delete multiple assistants by their IDs.
    """
    try:
        valid_ids = []
        invalid_ids = []
        for assistant_id in item.ids:
            try:
                # Assuming is_id_valid returns an integer or can be cast to one if needed by delete_items_by_ids
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

        # Use the helper function for bulk delete
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


async def get_one(id: str, request: Request, db: AsyncSession) -> JSONResponse:
    """
    Get one assistant by ID.
    """
    try:
        # Validate ID
        valid_id = is_id_valid(id)

        # Get item
        item = await get_item(db, Assistant, valid_id)
        if not item:
            raise build_error_object(status.HTTP_404_NOT_FOUND, "Assistant not found")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "payload": item.to_dict()},
        )
    except Exception as e:
        return await handle_error(request, e)


async def list_all(request: Request, db: AsyncSession) -> JSONResponse:
    """
    List all assistants.
    """
    try:
        items = await get_all_items(db, Assistant)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "payload": [item.to_dict() for item in items]},
        )
    except Exception as e:
        return await handle_error(request, e)


async def list_paginated(
    request: Request, pagination: PaginationParams, db: AsyncSession
) -> JSONResponse:
    """
    List assistants with pagination.
    """
    try:
        # Pass the pagination model directly to check_query_string
        processed_query = await check_query_string(pagination, Assistant)
        result = await get_items(db, Assistant, request, processed_query)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result,
        )
    except Exception as e:
        return await handle_error(request, e)
