from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Request

from app.models.entity import Entity
from app.models.assistant import Assistant
from app.schemas.entity import EntityCreate, EntityUpdate, Entity as EntitySchema
from app.utils.db_helpers import (
    get_all_items,
    get_items,
    get_item,
    create_item,
    update_item,
    delete_item,
    check_query_string
)
from app.utils.error_handling import is_id_valid


async def create(entity_in: EntityCreate, assistant_id: str, db: AsyncSession):
    """
    Create a new entity for an assistant.
    """
    try:
        # Validate assistant ID
        valid_assistant_id = is_id_valid(assistant_id)
        
        # Check if assistant exists
        assistant = await get_item(db, Assistant, valid_assistant_id)
        if not assistant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
        
        # Create entity with assistant_id
        entity_data = entity_in.dict()
        entity_data["assistant_id"] = valid_assistant_id
        
        # Create item
        item = await create_item(db, Entity, entity_data)
        return {"ok": True, "payload": EntitySchema.from_orm(item)}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def update(id: str, entity_in: EntityUpdate, assistant_id: str, db: AsyncSession):
    """
    Update an entity for an assistant.
    """
    try:
        # Validate IDs
        valid_id = is_id_valid(id)
        valid_assistant_id = is_id_valid(assistant_id)
        
        # Check if assistant exists
        assistant = await get_item(db, Assistant, valid_assistant_id)
        if not assistant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
        
        # Get entity
        entity = await get_item(db, Entity, valid_id)
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
        
        # Check if entity belongs to assistant
        if entity.assistant_id != valid_assistant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Entity does not belong to this assistant")
        
        # Update item
        item = await update_item(db, Entity, valid_id, entity_in.dict(exclude_unset=True))
        return {"ok": True, "payload": EntitySchema.from_orm(item)}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def delete(id: str, assistant_id: str, db: AsyncSession):
    """
    Delete an entity for an assistant.
    """
    try:
        # Validate IDs
        valid_id = is_id_valid(id)
        valid_assistant_id = is_id_valid(assistant_id)
        
        # Check if assistant exists
        assistant = await get_item(db, Assistant, valid_assistant_id)
        if not assistant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
        
        # Get entity
        entity = await get_item(db, Entity, valid_id)
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
        
        # Check if entity belongs to assistant
        if entity.assistant_id != valid_assistant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Entity does not belong to this assistant")
        
        # Delete item
        item = await delete_item(db, Entity, valid_id)
        return {"ok": True, "message": "Entity deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_one(id: str, assistant_id: str, db: AsyncSession):
    """
    Get an entity by ID for an assistant.
    """
    try:
        # Validate IDs
        valid_id = is_id_valid(id)
        valid_assistant_id = is_id_valid(assistant_id)
        
        # Check if assistant exists
        assistant = await get_item(db, Assistant, valid_assistant_id)
        if not assistant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
        
        # Get entity
        entity = await get_item(db, Entity, valid_id)
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
        
        # Check if entity belongs to assistant
        if entity.assistant_id != valid_assistant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Entity does not belong to this assistant")
        
        return {"ok": True, "payload": EntitySchema.from_orm(entity)}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def lists(request: Request, assistant_id: str, db: AsyncSession):
    """
    List all entities for an assistant.
    """
    try:
        # Validate assistant ID
        valid_assistant_id = is_id_valid(assistant_id)
        
        # Check if assistant exists
        assistant = await get_item(db, Assistant, valid_assistant_id)
        if not assistant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
        
        # Get entities for assistant
        query_params = dict(request.query_params)
        processed_query = await check_query_string(query_params)
        
        # Add filter for assistant_id
        if "filters" not in processed_query:
            processed_query["filters"] = {}
        processed_query["filters"]["assistant_id"] = valid_assistant_id
        
        result = await get_items(db, Entity, request, processed_query)
        
        # Convert items to schema
        result.items = [EntitySchema.from_orm(item) for item in result.items]
        
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
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 