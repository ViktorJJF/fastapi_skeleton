"""
Entities routes.
"""
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import entities_controller
from app.database.connection import get_db
from app.schemas.entity import EntityCreate, EntityUpdate
from app.utils.error_handling import handle_error

router = APIRouter()

@router.get("/{assistant_id}/entities", response_model=dict)
async def entities_list(
    assistant_id: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    List all entities for an assistant.
    """
    try:
        return await entities_controller.lists(request, assistant_id, db)
    except Exception as error:
        return handle_error(response, error)

@router.post("/{assistant_id}/entities", response_model=dict, status_code=status.HTTP_201_CREATED)
async def entities_create(
    assistant_id: str,
    entity_in: EntityCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new entity for an assistant.
    """
    try:
        return await entities_controller.create(entity_in, assistant_id, db)
    except Exception as error:
        return handle_error(response, error)

@router.get("/{assistant_id}/entities/{id}", response_model=dict)
async def entities_get(
    assistant_id: str,
    id: str,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Get an entity by ID for an assistant.
    """
    try:
        return await entities_controller.get_one(id, assistant_id, db)
    except Exception as error:
        return handle_error(response, error)

@router.put("/{assistant_id}/entities/{id}", response_model=dict)
async def entities_update(
    assistant_id: str,
    id: str,
    entity_in: EntityUpdate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an entity for an assistant.
    """
    try:
        return await entities_controller.update(id, entity_in, assistant_id, db)
    except Exception as error:
        return handle_error(response, error)

@router.delete("/{assistant_id}/entities/{id}", response_model=dict)
async def entities_delete(
    assistant_id: str,
    id: str,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an entity for an assistant.
    """
    try:
        return await entities_controller.delete(id, assistant_id, db)
    except Exception as error:
        return handle_error(response, error) 