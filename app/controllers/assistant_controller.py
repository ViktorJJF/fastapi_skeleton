from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Request

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
from app.utils.error_handling import handle_error, is_id_valid


async def create(assistant_in: AssistantCreate, db: AsyncSession):
    """
    Create a new assistant.
    """
    try:
        # Create item
        item = await create_item(db, Assistant, assistant_in.dict())
        return {"ok": True, "payload": AssistantSchema.from_orm(item)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def update(id: str, assistant_in: AssistantUpdate, db: AsyncSession):
    """
    Update an assistant.
    """
    try:
        # Validate ID
        valid_id = is_id_valid(id)
        
        # Update item
        item = await update_item(db, Assistant, valid_id, assistant_in.dict(exclude_unset=True))
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
        
        return {"ok": True, "payload": AssistantSchema.from_orm(item)}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def delete(id: str, db: AsyncSession):
    """
    Delete an assistant.
    """
    try:
        # Validate ID
        valid_id = is_id_valid(id)
        
        # Delete item
        item = await delete_item(db, Assistant, valid_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
        
        return {"ok": True, "message": "Assistant deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_one(id: str, db: AsyncSession):
    """
    Get an assistant by ID.
    """
    try:
        # Validate ID
        valid_id = is_id_valid(id)
        
        # Get item
        item = await get_item(db, Assistant, valid_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
        
        return {"ok": True, "payload": AssistantSchema.from_orm(item)}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def list_all(request: Request, db: AsyncSession):
    """
    List all assistants.
    """
    try:
        items = await get_all_items(db, Assistant)
        return {"ok": True, "payload": [AssistantSchema.from_orm(item) for item in items]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def list_paginated(request: Request, db: AsyncSession):
    """
    List assistants with pagination.
    """
    try:
        query_params = dict(request.query_params)
        processed_query = await check_query_string(query_params)
        result = await get_items(db, Assistant, request, processed_query)
        
        # Convert items to schema
        result.items = [AssistantSchema.from_orm(item) for item in result.items]
        
        return {
            "ok": True,
            "payload": {
                "items": result.items,
                "total": result.total,
                "page": result.page,
                "size": result.size,
                "pages": result.pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 