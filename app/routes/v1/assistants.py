"""
Assistants routes.
"""
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import assistant_controller
from app.db.session import get_db
from app.schemas.assistant import AssistantCreate, AssistantUpdate
from app.utils.error_handling import handle_error

router = APIRouter()

@router.get("/", response_model=dict)
async def list_assistants(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    List all assistants.
    """
    try:
        return await assistant_controller.list_all(request, db)
    except Exception as error:
        return handle_error(response, error)

@router.get("/paginated", response_model=dict)
async def list_assistants_paginated(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    List assistants with pagination.
    """
    try:
        return await assistant_controller.list_paginated(request, db)
    except Exception as error:
        return handle_error(response, error)

@router.get("/{id}", response_model=dict)
async def get_assistant(
    id: str,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Get an assistant by ID.
    """
    try:
        return await assistant_controller.get_one(id, db)
    except Exception as error:
        return handle_error(response, error)

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_assistant(
    assistant_in: AssistantCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new assistant.
    """
    try:
        return await assistant_controller.create(assistant_in, db)
    except Exception as error:
        return handle_error(response, error)

@router.put("/{id}", response_model=dict)
async def update_assistant(
    id: str,
    assistant_in: AssistantUpdate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an assistant.
    """
    try:
        return await assistant_controller.update(id, assistant_in, db)
    except Exception as error:
        return handle_error(response, error)

@router.delete("/{id}", response_model=dict)
async def delete_assistant(
    id: str,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an assistant.
    """
    try:
        return await assistant_controller.delete(id, db)
    except Exception as error:
        return handle_error(response, error) 