from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse

from app.models.assistant import Assistant
from app.schemas.assistant import AssistantCreate, AssistantUpdate, Assistant as AssistantSchema
from app.utils.db_helpers import (
    get_all_items,
    get_items,
    get_item,
    create_item,
    update_item,
    delete_item,
    check_query_string
)
from app.utils.error_handling import handle_error, is_id_valid, build_error_object


async def create(assistant_in: AssistantCreate, request: Request, db: AsyncSession) -> JSONResponse:
    """
    Create a new assistant.
    """
    try:
        # Create item
        item = await create_item(db, Assistant, assistant_in)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"ok": True, "payload": item.to_dict()}
        )
    except Exception as e:
        return await handle_error(request, e)


async def update(id: str, assistant_in: AssistantUpdate, request: Request, db: AsyncSession) -> JSONResponse:
    """
    Update an assistant.
    """
    try:
        # Validate ID
        valid_id = is_id_valid(id)
        
        # Update item
        item = await update_item(db, Assistant, valid_id, assistant_in)
        if not item:
            raise build_error_object(status.HTTP_404_NOT_FOUND, "Assistant not found")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "payload": item.to_dict()}
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
            content={"ok": True, "payload": {"id": valid_id, "deleted": True}}
        )
    except Exception as e:
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
            content={"ok": True, "payload": item.to_dict()}
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
            content={"ok": True, "payload": [item.to_dict() for item in items]}
        )
    except Exception as e:
        return await handle_error(request, e)


async def list_paginated(request: Request, db: AsyncSession) -> JSONResponse:
    """
    List assistants with pagination.
    """
    try:
        query_params = dict(request.query_params)
        processed_query = await check_query_string(query_params)
        result = await get_items(db, Assistant, request, processed_query)
        
        # Convert items using to_dict
        result_items = [item.to_dict() for item in result.items]
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "ok": True,
                "payload": {
                    "items": result_items,
                    "total": result.total,
                    "page": result.page,
                    "size": result.size,
                    "pages": result.pages
                }
            }
        )
    except Exception as e:
        return await handle_error(request, e) 