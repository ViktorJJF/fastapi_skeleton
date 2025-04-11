"""
Assistants routes.
"""
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import assistant_controller
from app.database.connection import get_db
from app.schemas.assistant import AssistantCreate, AssistantUpdate

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
    return await assistant_controller.list_all(request, db)

@router.get("/paginated", response_model=dict)
async def list_assistants_paginated(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    List assistants with pagination.
    """
    return await assistant_controller.list_paginated(request, db)

@router.get("/{id}", response_model=dict)
async def get_assistant(
    request: Request,
    response: Response,
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get an assistant by ID.
    """
    return await assistant_controller.get_one(id, db)

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_assistant(
    request: Request,
    response: Response,
    assistant: AssistantCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new assistant.
    """
    return await assistant_controller.create(assistant, db)

@router.put("/{id}", response_model=dict)
async def update_assistant(
    request: Request,
    response: Response,
    id: int,
    assistant: AssistantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an assistant.
    """
    return await assistant_controller.update(id, assistant, db)

@router.delete("/{id}", response_model=dict)
async def delete_assistant(
    request: Request,
    response: Response,
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an assistant.
    """
    return await assistant_controller.delete(id, db) 